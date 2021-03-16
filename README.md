# Turbo View Mixins for Django

This is an experimental Python module (`turbo.py`) which tries to
integrate [Turbo](https://turbo.hotwire.dev/) request handling to
Django Class-Based Views using mixins and additional templates.

There's no PyPI package because this should be simple enough to
just copy the file into project.


## What does it do?

- Adds middleware component which **detects** if a request is coming from **Turbo**
  and **modifies** a response to have a correct **status code** and **content type**.
- Adds concept of a **partial template** which will be used for
  Turbo requests.
- Adds concept of a **success template** which will be used for
  Turbo requests after a form is validated.
- Does not break existing Class-Based Views' functionality when Turbo
  is not used. Also works without JavaScript.


## What this is not?

- This is not a reference how Turbo support should be done in Django.
- This is not a fully baked library with all kind of fancy abstractions.


## Installation

1. Copy the `turbo.py` into your project

2. Add middleware to your settings

```python
MIDDLEWARE = [
    # ...
    "turbo.TurboMiddleware",
    " ...
]
```

3. Add mixins to your views

```python
from turbo import TurboFormViewMixin

class MyItemUpdateView(TurboFormViewMixin, UpdateView):
    queryset = MyItem.objects.all()
    form_class = MyItemForm
```


## Templates

> If you don't define `partial_template_name` or `success_template_name`
> they will be derived from `template_name`.

```python
template_name = "myapp/myitem_form.html"
partial_template_name = "myapp/_myitem_form.html"
success_template_name = "myapp/_myitem_form_success.html"
```

To disable the success template and revert back to original behaviour
(which is `HttpResponseRedirect`) set `success_template_name` as `None`.


## How to use

> See also included example project.

```python
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from turbo import TurboViewMixin, TurboFormViewMixin, TurboDeleteViewMixin

from .forms import MyItemForm
from .models import MyItem


class MyItemDetailView(TurboViewMixin, DetailView):
    model = MyItem


class MyItemCreateView(TurboFormViewMixin, CreateView):
    form_class = MyItemForm
    template_name = "myapp/myitem_add.html"


class MyItemUpdateView(TurboFormViewMixin, UpdateView):
    queryset = MyItem.objects.all()
    form_class = MyItemForm


class MyItemDeleteView(TurboDeleteViewMixin, DeleteView):
    queryset = MyItem.objects.all()

    # Used only for non-Turbo requests
    success_url = reverse_lazy("index")
```

#### `myapp/myitem_form.html`

This is a typical Django template used for non-Turbo requests.
Into this template we include the partial template.

```html
{% extends "base.html" %}

{% block content %}
  {% include "myapp/_myitem_form.html" include_turbo_stream=False %}
{% endblock %}
```

#### `myapp/_myitem_form.html`

This is the partial template used for Turbo requests.

> There's a variable named `include_turbo_stream` which is used to toggle
> `turbo-stream` element on and off.
> We want the element to show up only when a request is made by Turbo
> and the template is the "main" template used. That means we can
> disable the `turbo-stream` element when including this template
> into non-Turbo requests or inside other `turbo-stream` elements.
> See how this is used in other templates.

```html
{% if include_turbo_stream %}
<turbo-stream action="replace" target="myitem-{{ myitem.id }}">
  <template>
{% endif %}

<turbo-frame id="myitem-{{ myitem.id }}">
  <form method="post" action="{% url 'myitem-edit' myitem.id %}">
    {% csrf_token %}
    {{ form.as_ul }}
    <button>Save</button>
  </form>
</turbo-frame>

{% if include_turbo_stream %}
  </template>
</turbo-stream>
{% endif %}
```

#### `myapp/_myitem_form_success.html`

```html
<!-- Replace element #myitem-<id> -->
<turbo-stream action="replace" target="myitem-{{ myitem.id }}">
  <template>
    {% include "myapp/_myitem_detail.html" with include_turbo_stream=False %}
  </template>
</turbo-stream>

<!-- Append a message into element #messages -->
<turbo-stream action="append" target="messages">
  <template>
    <li class="info">Updated "{{ myitem }}"</li>
  </template>
</turbo-stream>
```

#### `myapp/_myitem_detail.html`

```html
{% if include_turbo_stream %}
<turbo-stream action="replace" target="myitem-{{ myitem.id }}">
  <template>
{% endif %}

<turbo-frame id="myitem-{{ myitem.id }}">
  <h1>{{ myitem }}</h1>
  <a href="{% url 'myitem-edit' myitem.id %}">Edit</a>
  <a href="{% url 'myitem-delete' myitem.id %}">Delete</a>
</turbo-frame>

{% if include_turbo_stream %}
  </template>
</turbo-stream>
{% endif %}
```


## Try the example project

Clone this repo and run...

```sh
cd example
python -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
cp ../turbo.py .
./manage.py migrate
./manage.py runserver
```
