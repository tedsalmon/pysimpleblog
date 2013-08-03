{% extends "admin/main.tpl" %}
{% block admin %}
<header>
    <hgroup>
        <h2>Global Settings</h2>
    </hgroup>
</header>
<hr />
<form class="form-horizontal">
{% for key, val in settings.items() %}
{% set name=key.replace('_',' ').title() %}
    <div class="control-group">
        <label class="control-label" for="settings_{{key}}">{{name}}</label>
        <div class="controls">
            <h id="settings_{{key}}" title="Click to edit" class="edit-settings editable" data-name="{{name}}" data-type="text">{{val}}</h>
        </div>
    </div>
{%endfor%}
</form>
{% endblock %}