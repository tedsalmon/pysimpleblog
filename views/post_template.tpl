{% set year = post['date'].strftime('%Y') %}    
    <header>
        <hgroup>
            <h2>{% if post_show_link %}<a class="muted" href="/{{year}}/{{post['url']}}">{{post['title']}}</a>{%else%}{{post['title']}}{%endif%}</h2>
            {% if not post['status'] %}<h5>Waring: DRAFT</h5>{% endif %}
            <h5>by {{post['author']}} on {{post['date'].strftime('%B %d, %Y %H:%M')}}</h5>
            {% if user_id %}
            <div class="blog-post-control">
                <a title="Edit Post" class="icon-edit" href="/admin/post-editor/{{post['_id']}}"></a>
                <a title="Delete Post" class=" delete-post icon-ban-circle" href="#" data-post-id="{{post['_id']}}"></a>
            </div>
            {% endif %}
        </hgroup>
    </header>
    <div>{{post['body']}}</div>