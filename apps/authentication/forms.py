from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, IntegerField
from wtforms.validators import Email, DataRequired


# login and registration


class LoginForm(FlaskForm):
    username = StringField("Username", id="username_login", validators=[DataRequired()])
    password = PasswordField("Password", id="pwd_login", validators=[DataRequired()])


class SageOneLoginForm(FlaskForm):
    username = StringField("username", id="sageusername", validators=[DataRequired()])
    password = StringField("password", id="sagepassword", validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    first_name = StringField(
        "first_name", id="first_name_create", validators=[DataRequired()]
    )
    last_name = StringField(
        "last_name", id="last_name_create", validators=[DataRequired()]
    )
    email = StringField(
        "Email", id="email_create", validators=[DataRequired(), Email()]
    )
    password = PasswordField("Password", id="pwd_create", validators=[DataRequired()])
    confirm_password = PasswordField("Password", id="cnf_pwd_create", validators=[DataRequired()])


class CreateJobForm(FlaskForm):
    name = StringField("name", id="username_create", validators=[DataRequired()])
    description = StringField(
        "description", id="description", validators=[DataRequired()]
    )
    input_tool = IntegerField(
        "input_tool", id="input_tool", validators=[DataRequired()]
    )
    output_tool = IntegerField(
        "output_tool", id="output_tool", validators=[DataRequired()]
    )
    is_active = BooleanField("is_active", id="is_active", validators=[DataRequired()])



class CreateSelectidForm(FlaskForm):
    id_select = StringField(
        "id", id="id_select", validators=[DataRequired()]
    )
    
   

class CreateSettingForm(FlaskForm):
    name = StringField("name", id="name", validators=[DataRequired()])
    username = StringField(
        "username", id="username", validators=[DataRequired(), Email()]
    )
    password = StringField("password", id="password", validators=[DataRequired()])
    client_id = StringField("client_id", id="client_id", validators=[DataRequired()])
    secret_key = StringField("secret_key", id="secret_key", validators=[DataRequired()])
    api_url = StringField("api_url", id="api_url", validators=[DataRequired()])
    api_version = StringField(
        "api_version", id="api_version", validators=[DataRequired()]
    )
    is_active = BooleanField("is_active", id="is_active", validators=[DataRequired()])

class CreateIdNameForm(FlaskForm):
    Email = StringField("name", id="name", validators=[DataRequired()])
    client_id = StringField("client_id", id="client_id", validators=[DataRequired()])
    client_secret = StringField("client_secret", id="client_secret", validators=[DataRequired()])

class CreateauthcodeForm(FlaskForm):
    auth_code = StringField(
        "auth_code", id="auth_code", validators=[DataRequired()]
    )
   

class CreateEmailForm(FlaskForm):
    email_input_tool = StringField(
        "input_tool", id="input_tool", validators=[DataRequired()]
    )


class CreateCustomerInfoForm(FlaskForm):
    Email = StringField("Email", id="Email", validators=[DataRequired()])
    Company = StringField("Company", id="Company", validators=[DataRequired()])
    First_Name = StringField("First_Name", id="First_Name", validators=[DataRequired()])
    Last_Name = StringField("Last_Name", id="Last_Name", validators=[DataRequired()])

class CreateFileInfoForm(FlaskForm):
    File_Name = StringField("File_Name", id="File_Name", validators=[DataRequired()])
   

class CreateXeroToolSettingForm(FlaskForm):

    name = StringField("name", id="name", validators=[DataRequired()])
    account_type = StringField("account_type", id="account_type", validators=[DataRequired()])
    tool_type = StringField("tool_type", id="tool_type", validators=[DataRequired()])
    client_id = StringField("client_id", id="client_id", validators=[DataRequired()])
    client_secret = StringField("client_secret", id="client_secret", validators=[DataRequired()])
    refresh_token = StringField("refresh_token", id="refresh_token", validators=[DataRequired()])
    access_token = StringField("access_token", id="access_token", validators=[DataRequired()])
    xero_tenant_id = StringField("xero_tenant_id", id="xero_tenant_id", validators=[DataRequired()])
    state = StringField("state", id="state", validators=[DataRequired()])
    scopes = StringField("scopes", id="scopes", validators=[DataRequired()])
    redirect_uri = StringField("redirect_uri", id="redirect_uri", validators=[DataRequired()])
    
class CreateCustomerInfoForm(FlaskForm):
    Email = StringField("Email", id="Email", validators=[DataRequired()])
    Company = StringField("Company", id="Company", validators=[DataRequired()])
    First_Name = StringField("First_Name", id="First_Name", validators=[DataRequired()])
    Last_Name = StringField("Last_Name", id="Last_Name", validators=[DataRequired()])

class CreateGetdataForm(FlaskForm):
    job_id = StringField("job_id", id="job_id", validators=[DataRequired()])
    table_data = StringField("table_data", id="table_data", validators=[DataRequired()])
    
class CreateToolFileInfoForm(FlaskForm):
    Email = StringField("Email", id="Email")
    File_Name = StringField("File_Name", id="File_Name", validators=[DataRequired()])
   