from django import forms

from .models import Mailing, MailingRecipients, Message


class BaseStyledForm(forms.ModelForm):
    """Базовый класс для единообразного стиля всех форм"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({"class": "form-control"})


class MailingRecipientsForm(BaseStyledForm):
    """Форма для получателей"""

    class Meta:
        model = MailingRecipients
        fields = ['email', 'full_name', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({"placeholder": "Email получателя"})
        self.fields["full_name"].widget.attrs.update({"placeholder": "Полное имя"})
        self.fields["comment"].widget.attrs.update({"placeholder": "Комментарий"})


class MessageForm(BaseStyledForm):
    """Форма для сообщений"""

    class Meta:
        model = Message
        fields = ['header', 'body']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["header"].widget.attrs.update({"placeholder": "Заголовок сообщения"})
        self.fields["body"].widget.attrs.update({"placeholder": "Текст сообщения"})


class MailingForm(BaseStyledForm):
    class Meta:
        model = Mailing
        fields = ['start', 'end', 'message', 'recipients']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        datetime_attrs = {
            "class": "form-control",
            "type": "datetime-local",
            "placeholder": "Пример: 10.12.25 15:00"
        }

        self.fields["start"].widget = forms.DateTimeInput(attrs=datetime_attrs, format="%Y-%m-%dT%H:%M")
        self.fields["end"].widget = forms.DateTimeInput(attrs=datetime_attrs, format="%Y-%m-%dT%H:%M")

        # чтобы Django принимал формат "10.12.25 15:00"
        self.fields["start"].input_formats = ["%Y-%m-%dT%H:%M", "%d.%m.%y %H:%M"]
        self.fields["end"].input_formats = ["%Y-%m-%dT%H:%M", "%d.%m.%y %H:%M"]

        self.fields["recipients"].widget.attrs.update({"size": 5})
