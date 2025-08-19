# 第 10 章：邮件

在本章中，我们将完全配置邮件功能，并添加密码更改和密码重置功能。目前邮件实际上并没有发送给用户，它们只是输出到我们的命令行控制台。我们将通过注册第三方邮件服务、获取 API 密钥并更新我们的 `django_project/settings.py` 文件来改变这一点。Django 会处理其余的工作。

到目前为止，我们所有的工作——自定义用户模型、页面应用、静态资源、使用 allauth 的身份验证和环境变量——几乎可以应用于任何新项目。在本章之后，我们将开始构建书店网站本身，而不是基础步骤。

## 1. 自定义确认邮件

让我们注册一个新的用户账户来查看当前的用户注册流程，然后我们将对其进行自定义。确保您已注销，然后导航到注册页面。我选择使用 `testuser3@email.com` 和 `testpass123` 作为密码。

提交后，我们被重定向到主页，显示自定义问候语，并在命令行控制台中向我们发送一封邮件。您可以通过使用 `docker-compose logs` 检查日志来查看这一点。以下是更长输出的片段。

**Shell**

```bash
$ docker-compose logs
...
Hello from example.com!

| You're receiving this e-mail because user testuser3 ...
...
```

要自定义此邮件，我们首先需要找到现有的模板。导航到 Github 上的 django-allauth 源代码，并使用生成文本的一部分进行搜索。例如，"You're receiving this e-mail."。这导致发现了一个位于 `django-allauth/allauth/templates/account/email` 中的 `email_confirmation_message.txt` 文件。如果您查看此目录的内容，还有一个主题行文件 `email_confirmation_subject.txt`，我们可以并且将要更改它。

要自定义这些文件，我们将通过在项目中重新创建 django-allauth 的相同结构来覆盖它们。这意味着在 `templates/account` 目录中创建一个 `email` 目录。

```bash
$ mkdir templates/account/email
```

然后在文本编辑器中创建两个新文件：

- `templates/account/email/email_confirmation_subject.txt`
- `templates/account/email/email_confirmation_message.txt`

让我们从主题行开始，因为它是两者中较短的一个。以下是来自 django-allauth 的默认文本。

**email_confirmation_subject.txt**

```django
{% load i18n %}
{% autoescape off %}
{% blocktrans %}Please Confirm Your E-mail Address{% endblocktrans %}
{% endautoescape %}
```

第一行 `{% load i18n %}` 是为了支持 Django 的国际化功能，该功能支持多种语言。然后是用于自动转义的 Django 模板标签。默认情况下它是"开启"的，可以防止跨站脚本攻击等安全问题。但是由于我们可以信任这里的文本内容，所以将其关闭。

最后，我们来到文本本身，它被包装在 `blocktrans` 模板标签中以支持翻译。让我们将文本从"E-mail Address"更改为"Sign Up"来演示我们可以做到这一点。

**email_confirmation_subject.txt**

```django
{% load i18n %}
{% autoescape off %}
{% blocktrans %}Confirm Your Sign Up{% endblocktrans %}
{% endautoescape %}
```

现在转到邮件确认消息本身。以下是当前的默认值：

**email_confirmation_message.txt**

```django
{% extends "account/email/base_message.txt" %}
{% load account %}
{% load i18n %}

{% block content %}{% autoescape off %}{% user_display user as user_display %}\
{% blocktrans with site_name=current_site.name site_domain=current_site.domain %}\
You're receiving this e-mail because user {{ user_display }} has given your\
e-mail address to register an account on {{ site_domain }}.

To confirm this is correct, go to {{ activate_url }}\
{% endblocktrans %}{% endautoescape %}{% endblock %}
```

请注意，反斜杠 `\` 是为了格式化而包含的，但在原始代码中不是必需的。换句话说，您可以根据需要从下面的代码（和其他代码示例）中删除它们。

您可能注意到发送的默认邮件将我们的网站称为 `example.com`，这里显示为 `{{ site_name }}`。这来自哪里？答案是 Django 管理员的站点部分，django-allauth 使用它。所以前往 `http://127.0.0.1:8000/admin/` 的管理员页面，并点击主页上的 Sites 链接。

这里有一个"Domain Name"和一个"Display Name"。点击"Domain Name"下的 `example.com` 以便我们可以编辑它。Domain Name 是站点的完整域名，例如可能是 `djangobookstore.com`，而 Display Name 是站点的人类可读名称，例如 Django Bookstore。

进行这些更新，完成后点击右下角的"Save"按钮。

好的，回到我们的邮件。让我们稍微自定义一下。在第一行，我们可以看到这封邮件实际上扩展了另一个模板——`base_message.txt`——它包含"Hello from…"的初始问候语。要更新它，我们只需要在 email 文件夹中添加一个 `base_message.txt` 文件。由于这只是为了演示目的，尝试将"You're"更改为"You are"来证明我们可以自定义文本。

**email_confirmation_message.txt**

```django
{% extends "account/email/base_message.txt" %}
{% load account %}
{% load i18n %}

{% block content %}{% autoescape off %}{% user_display user as user_display %}\
{% blocktrans with site_name=current_site.name site_domain=current_site.domain %}\
You are receiving this e-mail because user {{ user_display }} has given your \
e-mail address to register an account on {{ site_domain }}.

To confirm this is correct, go to {{ activate_url }}\
{% endblocktrans %}{% endautoescape %}{% endblock %}
```

最后一项要更改的内容。您是否注意到邮件来自 `webmaster@localhost`？这是一个默认设置，我们也可以通过 `DEFAULT_FROM_EMAIL` 更新它。让我们现在通过在 `django_project/settings.py` 文件底部添加以下行来做到这一点。

```python
# django_project/settings.py

DEFAULT_FROM_EMAIL = "admin@djangobookstore.com"  # new
```

确保您已从网站注销，然后再次转到注册页面创建新用户。为了方便起见，我使用了 `testuser4@email.com`。

注册后被重定向到主页，通过输入 `docker-compose logs` 检查命令行以查看消息。

```bash
...
web_1 | Content-Transfer-Encoding: 7bit
web_1 | Subject: [Django Bookstore] Confirm Your Sign Up
web_1 | From: admin@djangobookstore.com
web_1 | To: testuser4@email.com
web_1 | Date: Tue, 17 May 2022 18:34:50 -0000
web_1 | Message-ID: <156312929025.27.2332096239397833769@87d045aff8f7>
web_1 |
web_1 | Hello from Django Bookstore!
web_1 |
web_1 | You are receiving this e-mail because user testuser4 has given your\
web_1 | e-mail address to register an account on djangobookstore.com.
web_1 |
web_1 | To confirm this is correct, go to http://127.0.0.1:8000/accounts/\
web_1 | confirm-email/Mg:1nr527:FhQTQdZha_1mIsF9B5--71pfMDNlnR2vy4-sTrFmAyQ/
web_1 |
web_1 | Thank you from Django Bookstore!
web_1 | djangobookstore.com
```

就是这样，有了新的 From 设置、新的域名 `djangobookstore.com` 和邮件中的新消息。

## 2. 邮件确认页面

点击邮件中的唯一 URL 链接，它会重定向到邮件确认页面。

不是很吸引人。让我们更新它以匹配我们网站其余部分的外观。再次在 Github 上的 django-allauth 源代码中搜索，发现此文件的名称和位置是 `templates/account/email_confirm.html`。所以让我们创建一个同名的模板文件，然后更新它以扩展 `_base.html` 并为按钮使用 Bootstrap。

```html
<!-- templates/account/email_confirm.html -->

{% extends "_base.html" %} {% load i18n %} {% load account %} {% block
head_title %}{% trans "Confirm E-mail Address" %}{% endblock %} {% block content
%}

<h1>{% trans "Confirm E-mail Address" %}</h1>
{% if confirmation %} {% user_display confirmation.email_address.user as
user_display %}
<p>
  {% blocktrans with confirmation.email_address.email as email %}Please confirm
  that <a href="mailto:{{ email }}">{{ email }}</a> is an e-mail address for
  user {{ user_display }}.{% endblocktrans %}
</p>
<form method="post" action="{% url 'account_confirm_email' confirmation.key %}">
  {% csrf_token %}
  <button class="btn btn-primary" type="submit">{% trans 'Confirm' %}</button>
</form>
{% else %} {% url 'account_email' as email_url %}
<p>
  {% blocktrans %}This e-mail confirmation link expired or is invalid. Please
  <a href="{{ email_url }}">issue a new e-mail confirmation request</a>.\ {%
  endblocktrans %}
</p>
{% endif %} {% endblock %}
```

刷新页面以查看我们的更新。

## 3. 密码重置和密码更改

Django 和 django-allauth 还支持其他用户账户功能，例如重置忘记的密码和在已登录时更改现有密码的能力。

默认密码重置和密码更改页面的位置如下：

- `http://127.0.0.1:8000/accounts/password/reset/`
- `http://127.0.0.1:8000/accounts/password/change/`

如果您完成每个流程，您可以在 django-allauth 源代码中找到相应的模板和邮件消息。

## 4. 邮件服务

到目前为止我们配置的邮件通常被称为"事务性邮件"，因为它们基于某种用户操作而发生。这与"营销邮件"形成对比，例如月度通讯。

有许多事务性邮件提供商可用，包括 SendGrid、MailGun、Amazon 的 Simple Email Service。Django 对使用哪个提供商是不可知的；所有提供商的步骤都相似，许多都有免费层可用。

在注册您选择的邮件服务账户后，您通常可以选择使用 SMTP 或 Web API。SMTP 更容易配置，但 Web API 更可配置和健壮。从 SMTP 开始，然后从那里开始：邮件配置本身可能相当复杂。

在从邮件提供商获得用户名和密码后，一些设置调整将允许 Django 使用它们发送邮件。

第一步是更新 `EMAIL_BACKEND` 配置，它应该在 `django_project/settings.py` 文件的底部附近，因为我们之前在 django-allauth 配置部分更新了它。

```python
# django_project/settings.py

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"  # new
```

这意味着邮件将不再输出到命令行控制台，而是尝试连接到 SMTP 服务器。然后根据您的邮件提供商的说明，将 `EMAIL_HOST`、`EMAIL_HOST_USER`、`EMAIL_HOST_PASSWORD`、`EMAIL_PORT` 和 `EMAIL_USE_TLS` 配置为环境变量。

在官方源代码中，`EMAIL_BACKEND` 将保持控制台，但前面的步骤是如何添加邮件服务。如果您发现自己在正确配置邮件方面感到沮丧，嗯，您并不孤单！Django 至少使它比在没有包含电池的框架的好处下实现要容易得多。

## 5. Git

要提交本章的代码更新，请确保检查更改的状态，添加所有更改，并包含提交消息。

**Shell**

```bash
$ git status
$ git add .
$ git commit -m 'ch10'
```

如果您有任何问题，请将您的代码与 Github 上的官方源代码进行比较。

## 6. 结论

正确配置邮件在很大程度上是一次性的痛苦。但它是任何生产网站的必要部分。这结束了我们书店项目的基础章节。在下一章中，我们将最终开始构建书店本身。
