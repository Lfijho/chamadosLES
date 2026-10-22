from flask_wtf import FlaskForm
from wtforms import PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from .models import CATEGORIES, COLUMNS


def stripped(value):
    return value.strip() if value else value


class PortugueseSelectField(SelectField):
    def pre_validate(self, form):
        try:
            super().pre_validate(form)
        except ValidationError as error:
            raise ValidationError("Selecione uma opção válida.") from error


class LoginForm(FlaskForm):
    email = StringField("E-mail", filters=[stripped], validators=[
        DataRequired(message="Informe seu e-mail."),
        Length(max=254, message="Use no máximo 254 caracteres."),
        Email(message="Informe um e-mail válido."),
    ])
    password = PasswordField("Senha", validators=[
        DataRequired(message="Informe sua senha."),
        Length(max=128, message="Use no máximo 128 caracteres."),
    ])


class TicketForm(FlaskForm):
    title = StringField("Título", filters=[stripped], validators=[
        DataRequired(message="Informe o título."),
        Length(min=5, max=120, message="O título deve ter de 5 a 120 caracteres."),
    ])
    category = PortugueseSelectField("Categoria", choices=[("", "Selecione uma categoria")] + [(x, x) for x in CATEGORIES],
                           validators=[DataRequired(message="Selecione uma categoria.")],
                           validate_choice=True)
    description = TextAreaField("Descrição", filters=[stripped], validators=[
        DataRequired(message="Descreva o problema."),
        Length(min=10, max=5000, message="A descrição deve ter de 10 a 5.000 caracteres."),
    ])


class MoveTaskForm(FlaskForm):
    column = PortugueseSelectField("Mover para", choices=[(x, x) for x in COLUMNS],
                         validators=[DataRequired(message="Selecione uma coluna.")])
