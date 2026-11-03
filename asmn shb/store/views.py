from datetime import datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, ProtectedError, Sum
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CategoryForm, ProductForm
from .models import Category, Order, OrderItem, PageView, Product


def home(request):
    PageView.objects.create()
    category = request.GET.get("category")
    query = request.GET.get("q", "").strip()
    return render(request, "store/home.html", {"categories": Category.objects.all(), "selected": category, "query": query})


def products_api(request):
    products = Product.objects.filter(is_active=True).select_related("category")
    category = request.GET.get("category")
    query = request.GET.get("q", "").strip()
    if category:
        products = products.filter(category__slug=category)
    if query:
        products = products.filter(name__icontains=query)
    return JsonResponse({"products": [{
        "id": product.id, "name": product.name, "description": product.description,
        "price": product.price, "old_price": product.old_price,
        "category": product.category.slug,
        "category_name": product.category.name,
        "image_url": request.build_absolute_uri(product.image.url) if product.image else "",
    } for product in products]})


def login_view(request):
    error = None
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username", ""),
            password=request.POST.get("password", ""),
        )
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "??? ?????? ?? ??? ???? ???? ????."
    return render(request, "store/login.html", {"error": error})

def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    now = timezone.localtime()
    today = now.date()
    daily_start = today - timedelta(days=29)
    month_start = (today.replace(day=1) - timedelta(days=335)).replace(day=1)
    year_start = today.replace(year=today.year - 4, month=1, day=1)
    tomorrow = today + timedelta(days=1)

    def chart_series(start, end, truncation, period, label_format):
        counts = {
            (row["period"].date() if isinstance(row["period"], datetime) else row["period"]): row["count"]
            for row in PageView.objects.filter(created_at__gte=start, created_at__lt=end)
            .annotate(period=truncation("created_at"))
            .values("period")
            .annotate(count=Count("pk"))
        }
        values = []
        cursor = period(start.date())
        last = period((end - timedelta(microseconds=1)).date())
        while cursor <= last:
            values.append({"label": label_format(cursor), "value": counts.get(cursor, 0)})
            if truncation is TruncDate:
                cursor += timedelta(days=1)
            elif truncation is TruncMonth:
                cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
            else:
                cursor = cursor.replace(year=cursor.year + 1)
        return values

    start_of_day = lambda value: timezone.make_aware(datetime.combine(value, time.min))
    daily = chart_series(start_of_day(daily_start), start_of_day(tomorrow), TruncDate, lambda value: value, lambda value: value.strftime("%d"))
    monthly = chart_series(start_of_day(month_start), start_of_day(tomorrow), TruncMonth, lambda value: value.replace(day=1), lambda value: str(value.month))
    yearly = chart_series(start_of_day(year_start), start_of_day(tomorrow), TruncYear, lambda value: value.replace(month=1, day=1), lambda value: str(value.year))
    orders = Order.objects.prefetch_related("items__product")
    active_items = OrderItem.objects.filter(order__status__in=[Order.Status.NEW, Order.Status.PREPARING, Order.Status.SENT, Order.Status.DELIVERED])
    sales = active_items.aggregate(value=Sum("quantity"))["value"] or 0
    revenue = active_items.aggregate(value=Sum(F("unit_price") * F("quantity")))["value"] or 0
    today_views = daily[-1]["value"] if daily else 0
    context = {
        "orders": orders[:10],
        "product_count": Product.objects.count(),
        "order_count": orders.count(),
        "new_count": orders.filter(status=Order.Status.NEW).count(),
        "visit_count": sum(row["value"] for row in daily),
        "average_visits": round(sum(row["value"] for row in daily) / len(daily), 1) if daily else 0,
        "today_views": today_views,
        "revenue": revenue,
        "sold_quantity": sales,
        "low_stock": Product.objects.filter(is_active=True, stock__lte=5).order_by("stock", "name")[:10],
        "chart_data": {"d": daily, "m": monthly, "y": yearly},
    }
    return render(request, "store/dashboard.html", context)


@login_required
def product_list(request):
    products = Product.objects.select_related("category").order_by("name")
    return render(request, "store/product_list.html", {"products": products})


@login_required
def category_list(request):
    next_page = request.GET.get("next")
    if next_page not in ("", "product_add"):
        next_page = ""
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "دسته‌بندی جدید اضافه شد.")
            if request.POST.get("next") == "product_add":
                return redirect("product_add")
            return redirect("category_list")
    elif request.method == "GET":
        form = CategoryForm()
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
    categories = Category.objects.annotate(product_count=Count("products")).order_by("name")
    return render(request, "store/category_list.html", {
        "form": form,
        "categories": categories,
        "next_page": next_page,
    })


@login_required
def product_edit(request, pk=None):
    product = get_object_or_404(Product, pk=pk) if pk is not None else None
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            clear_image = request.POST.get("clear_image") == "1" and not request.FILES.get("image")
            saved_product = form.save()
            if clear_image and saved_product.image:
                saved_product.image.delete(save=False)
                saved_product.image = ""
                saved_product.save(update_fields=["image"])
            messages.success(request, "محصول ذخیره شد.")
            return redirect("product_list")
    elif request.method == "GET":
        form = ProductForm(instance=product)
    else:
        return HttpResponseNotAllowed(["GET", "POST"])
    return render(request, "store/product_form.html", {"form": form, "product": product})


@login_required
def product_toggle(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=["is_active"])
    messages.success(request, "وضعیت نمایش محصول تغییر کرد.")
    return redirect("product_list")


@login_required
def product_delete(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    product = get_object_or_404(Product, pk=pk)
    try:
        product.delete()
    except ProtectedError:
        messages.error(request, "این محصول در سفارش ثبت شده و قابل حذف نیست.")
    else:
        messages.success(request, "محصول حذف شد.")
    return redirect("product_list")


@login_required
def order_list(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        if status not in Order.Status.values:
            messages.error(request, "وضعیت انتخاب‌شده معتبر نیست.")
        else:
            order = get_object_or_404(Order, pk=order_id)
            order.status = status
            order.save(update_fields=["status"])
            messages.success(request, f"وضعیت سفارش #{order.pk} به‌روز شد.")
        return redirect("order_list")
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET", "POST"])
    orders = Order.objects.prefetch_related("items__product")
    return render(request, "store/order_list.html", {"orders": orders, "statuses": Order.Status.choices})


def track_order(request):
    order = None
    error = None
    if request.method == "POST":
        number = request.POST.get("number", "").translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
        phone = request.POST.get("phone", "").translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
        if not number.isdecimal() or len(phone) != 4 or not phone.isdecimal():
            error = "شماره سفارش و چهار رقم آخر تلفن را بررسی کنید."
        else:
            order = Order.objects.filter(pk=number, phone__endswith=phone).first()
            if not order:
                error = "سفارشی با این اطلاعات پیدا نشد."
    status_steps = list(Order.Status.choices)[:-1]
    status_index = next((index for index, (status, _) in enumerate(status_steps) if order and order.status == status), 0)
    return render(request, "store/track.html", {
        "order": order, "error": error, "status_steps": status_steps, "status_index": status_index,
    })
