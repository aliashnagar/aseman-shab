from django.db import models


class Category(models.Model):
    name = models.CharField("نام", max_length=80, unique=True)
    slug = models.SlugField("شناسه", unique=True, allow_unicode=True)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self): return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="دسته‌بندی")
    name = models.CharField("نام محصول", max_length=160)
    description = models.TextField("توضیحات", blank=True)
    price = models.PositiveIntegerField("قیمت (تومان)")
    old_price = models.PositiveIntegerField("قیمت قبل", blank=True, null=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    image = models.ImageField("تصویر", upload_to="products/", blank=True)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصول‌ها"
        ordering = ["-created_at"]

    def __str__(self): return self.name


class PageView(models.Model):
    created_at = models.DateTimeField("زمان بازدید", auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = "بازدید صفحه"
        verbose_name_plural = "بازدیدهای صفحه"


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "جدید"
        PREPARING = "preparing", "در حال آماده‌سازی"
        SENT = "sent", "ارسال‌شده"
        DELIVERED = "delivered", "تحویل‌شده"
        CANCELLED = "cancelled", "لغوشده"
    customer_name = models.CharField("نام مشتری", max_length=120)
    phone = models.CharField("تلفن", max_length=20)
    address = models.TextField("نشانی")
    status = models.CharField("وضعیت", max_length=12, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("زمان ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ["-created_at"]

    def __str__(self): return f"سفارش #{self.pk} - {self.customer_name}"

    @property
    def total_amount(self):
        return sum(item.total for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.PositiveIntegerField()

    @property
    def total(self): return self.quantity * self.unit_price
