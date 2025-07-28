import re

from django import forms

from .models import Stock


class StockForm(forms.ModelForm):
    """
    銘柄追加用のフォーム
    """

    use_demo_data = forms.BooleanField(
        required=False,
        label="デモデータを使用",
        help_text="チェックするとデモデータを使用します（APIが利用できない場合にも有用）",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Stock
        fields = ["symbol", "name"]
        widgets = {
            "symbol": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "例: 7203 または 9984",
                    "maxlength": 10,
                    "pattern": "^[A-Za-z0-9]+$",
                    "title": "英数字のみ入力してください（カンマやスペースは不可）",
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "例: トヨタ自動車",
                    "maxlength": 100,
                }
            ),
        }
        labels = {"symbol": "ティッカーシンボル", "name": "銘柄名"}
        help_texts = {
            "symbol": "<strong>注意:</strong> 1つの銘柄のみ入力してください。日本株の場合は証券コード（例: 7203はトヨタ自動車）<br>複数の銘柄を追加したい場合は、個別に追加してください。",
            "name": "正式な銘柄名を入力してください。",
        }

    def clean_symbol(self):
        """
        ティッカーシンボルのカスタムバリデーション
        """
        symbol = self.cleaned_data.get("symbol", "").strip().upper()

        if not symbol:
            raise forms.ValidationError("ティッカーシンボルを入力してください。")

        # カンマやスペースのチェック
        if "," in symbol:
            raise forms.ValidationError(
                "ティッカーシンボルにカンマを含めることはできません。1つの銘柄のみ入力してください。"
            )

        if " " in symbol:
            raise forms.ValidationError(
                "ティッカーシンボルにスペースを含めることはできません。"
            )

        # 英数字のみのチェック
        if not re.match("^[A-Za-z0-9]+$", symbol):
            raise forms.ValidationError(
                "ティッカーシンボルは英数字のみで入力してください。"
            )

        # 長さのチェック
        if len(symbol) > 10:
            raise forms.ValidationError(
                "ティッカーシンボルは10文字以内で入力してください。"
            )

        # 重複チェック
        if Stock.objects.filter(symbol=symbol).exists():
            raise forms.ValidationError(f"銘柄 {symbol} は既に登録されています。")

        return symbol

    def clean_name(self):
        """
        銘柄名のカスタムバリデーション
        """
        name = self.cleaned_data.get("name", "").strip()

        if not name:
            raise forms.ValidationError("銘柄名を入力してください。")

        if len(name) > 100:
            raise forms.ValidationError("銘柄名は100文字以内で入力してください。")

        return name
