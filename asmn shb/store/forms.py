from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from .models import Category, Product


def _category_slug(name):
    return slugify(name, allow_unicode=True)[:50].rstrip("-")


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(attrs={"autofocus": True}),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError("این دسته‌بندی از قبل ثبت شده است.")
        slug = _category_slug(name)
        if not slug:
            raise ValidationError("نام دسته‌بندی باید شامل حروف یا عدد باشد.")
        if Category.objects.filter(slug=slug).exists():
            raise ValidationError("برای این نام، شناسهٔ دسته‌بندی تکراری است.")
        return name

    def save(self, commit=True):
        category = super().save(commit=False)
        category.slug = _category_slug(category.name)
        if commit:
            category.save()
        return category


class ProductForm(forms.ModelForm):
    discount_enabled = forms.BooleanField(label="اعمال تخفیف روی این محصول", required=False)
    discount_percent = forms.IntegerField(
        label="درصد تخفیف",
        required=False,
        min_value=1,
        max_value=90,
    )

    class Meta:
        model = Product
        fields = ("name", "category", "price", "stock", "image")
        widgets = {
            "price": forms.NumberInput(attrs={"min": 0}),
            "stock": forms.NumberInput(attrs={"min": 0}),
            "image": forms.FileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            discounted = bool(self.instance.old_price and self.instance.old_price > self.instance.price)
            self.fields["price"].initial = self.instance.old_price if discounted else self.instance.price
            self.fields["discount_enabled"].initial = discounted
            if discounted:
                self.fields["discount_percent"].initial = round(
                    (self.instance.old_price - self.instance.price) * 100 / self.instance.old_price
                )
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("discount_enabled") and cleaned_data.get("discount_percent") is None:
            self.add_error("discount_percent", "درصد تخفیف را بین ۱ تا ۹۰ وارد کنید.")
        return cleaned_data

    def save(self, commit=True):
        product = super().save(commit=False)
        base_price = self.cleaned_data["price"]
        if self.cleaned_data.get("discount_enabled"):
            discount_percent = self.cleaned_data["discount_percent"]
            product.old_price = base_price
            product.price = (base_price * (100 - discount_percent) + 50) // 100
        else:
            product.old_price = None
            product.price = base_price
        if commit:
            product.save()
            self.save_m2m()
        return product
