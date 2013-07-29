{% extends "base.tpl" %}
{% block body %}
<div class="blog-content divider-right span9">
{% for post in posts %}
    {% set year = post['date'].strftime('%Y') %}
    <article>
        {% set post_show_link = True %}
        {% include 'post_template.tpl' %}
        <div class="blog-tags"><b class="icon-tags" title="Tags"></b> {% for tag in post['tags'] %}{{'<a class="link-underline muted" href="/tags/%s">%s</a> ' % (tag.strip().replace(' ','-'), tag)}}{% endfor %}</div>
        <div class="blog-comment-count">
            <b class="icon-comment" title="Comments"></b>
            <a class="muted" href="/{{year}}/{{post['url']}}#comments">{{post['comment_count']}} comment{% if post['comment_count'] > 1 or post['comment_count'] == 0 %}s{%endif%}</a>
        </div>
    </article>
{% endfor %}
{% if posts|length == 10 %}
    <div class="blog-pagination" class="span11">
        <a class="muted" href='/page/{{page_id+1}}'>{{'\u2190'}} Older</a>
        {% if page_id > 1 %}
        <a class="muted" href='/page/{{page_id-1}}'>{{'\u2192'}} Newer</a>
        {% endif %}
    </div>
{% endif %}
</div>
<div class="blog-sidebar span3">
    <h3>Recent Posts</h3>
    <div>
        <ul class="blog-recent">
        {% for post in recent_posts%}
            <li><a class="muted" href="/{{post['date'].strftime('%Y')}}/{{post['url']}}">{{post['title']}}</a></li>
        {% endfor %}
        </ul>
    </div>
</div>
{% endblock %}