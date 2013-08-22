{% extends "admin/main.tpl" %}
{% block admin %}
<header>
    <hgroup>
        <h2>Global Settings</h2>
    </hgroup>
</header>
<hr />
<form class="form-horizontal">
{% for key in opts %}
{% set val = settings[key]%}
{% set name = key.replace('_',' ').title() %}
    <div class="control-group">
        <label class="control-label" for="settings_{{key}}">{{name}}</label>
        <div class="controls">
            {% if key != 'debug' %}
            <h id="settings_{{key}}" title="Click to edit" class="edit-settings editable" data-name="{{key}}" data-type="text">{{val}}</h>
            {%else %}
            <h id="settings_{{key}}" title="Click to edit" class="edit-settings-select editable" data-name="{{key}}" data-value={{val|int}} data-type="select" data-source="[{value: 1, text: 'True'},{value: 0, text: 'False'}]">{{val}}</h>
            {% endif %}
        </div>
    </div>
{%endfor%}
</form>
{% endblock %}