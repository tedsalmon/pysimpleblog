{% extends "base.tpl" %}
{% block body %}
<div class="blog-content">
    {% if not posts %}
    <h2>No posts tagged as "{{tag | e}}"</h2>
    {% else %}
    <h2>Posts tagged as {{tag | e}}:</h2>
    {% for post in posts %}
    <article>
        {% set post_show_link = True %}
        {% include 'post_template.tpl' %}
        <div class="blog-tags"><b class="icon-tags" title="Tags"></b> {% for tag in post['tags'] %}{{'<a class="blog-tag muted" href="/tags/%s">%s</a> ' % (tag.strip(), tag)}}{% endfor %}</div>
        <div class="blog-comment-count">
            <b class="icon-comment"></b>
            <a class="muted" href="/{{post['_id']}}/{{post['url_name']}}#comments">{{post['comment_count']}} comments</a>
        </div>
    </article>
    {% endfor %}
    {% endif %}
</div>
{% endblock %}