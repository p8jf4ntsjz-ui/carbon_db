from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (StringField, PasswordField, SelectField, FloatField,
                     IntegerField, TextAreaField, DateField, BooleanField,
                     MultipleFileField, SubmitField)
from wtforms.validators import (DataRequired, Email, Length, EqualTo,
                                NumberRange, Optional, ValidationError)
from app.models.user import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Mot de passe', validators=[DataRequired()])
    remember_me = BooleanField('Se souvenir de moi')
    submit = SubmitField('Se connecter')


class OpportunityForm(FlaskForm):
    # Step 1 — Client
    title = StringField('Titre', validators=[DataRequired(), Length(max=200)])
    client_name = StringField('Nom du client', validators=[DataRequired(), Length(max=150)])
    client_email = StringField('Email client', validators=[Optional(), Email(), Length(max=120)])
    client_phone = StringField('Téléphone', validators=[Optional(), Length(max=30)])
    client_company = StringField('Société', validators=[Optional(), Length(max=150)])
    client_sector = SelectField('Secteur', choices=[
        ('', '— Sélectionner —'),
        ('tech', 'Technologie'), ('finance', 'Finance'), ('sante', 'Santé'),
        ('industrie', 'Industrie'), ('retail', 'Retail'), ('services', 'Services'),
        ('immobilier', 'Immobilier'), ('autre', 'Autre'),
    ], validators=[Optional()])
    # Step 2 — Deal
    amount = FloatField('Montant (€)', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Statut', choices=[
        ('prospect', 'Prospect'), ('qualified', 'Qualifié'),
        ('proposal', 'Proposition'), ('negotiation', 'Négociation'),
        ('won', 'Gagné'), ('lost', 'Perdu'),
    ])
    priority = SelectField('Priorité', choices=[
        ('low', 'Faible'), ('medium', 'Moyenne'), ('high', 'Haute')
    ])
    probability = IntegerField('Probabilité (%)', validators=[NumberRange(min=0, max=100)], default=50)
    expected_close = DateField('Date de clôture prévue', validators=[Optional()])
    source = SelectField('Source', choices=[
        ('', '— Sélectionner —'),
        ('inbound', 'Inbound'), ('outbound', 'Outbound'),
        ('referral', 'Référence'), ('web', 'Site web'),
        ('event', 'Événement'), ('autre', 'Autre'),
    ], validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=2000)])
    # Step 3 — Fichiers
    attachments = MultipleFileField('Pièces jointes', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'],
                    'Formats autorisés : PDF, Word, Excel, images.')
    ])
    submit = SubmitField('Enregistrer')


class UserAdminForm(FlaskForm):
    name = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField('Rôle', choices=[
        ('user', 'Utilisateur'), ('manager', 'Manager'), ('admin', 'Admin')
    ])
    password = PasswordField('Mot de passe', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirmer', validators=[
        EqualTo('password', message='Les mots de passe ne correspondent pas.')
    ])
    is_active = BooleanField('Compte actif', default=True)
    submit = SubmitField('Enregistrer')

    def __init__(self, original_email=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, field):
        if field.data != self.original_email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Cet email est déjà utilisé.')


class ProfileForm(FlaskForm):
    name = StringField('Nom complet', validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Téléphone', validators=[Optional(), Length(max=30)])
    submit = SubmitField('Mettre à jour')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Mot de passe actuel', validators=[DataRequired()])
    new_password = PasswordField('Nouveau mot de passe', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmer', validators=[
        DataRequired(), EqualTo('new_password', message='Les mots de passe ne correspondent pas.')
    ])
    submit = SubmitField('Changer')