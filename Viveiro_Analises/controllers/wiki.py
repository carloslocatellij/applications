# -*- coding: utf-8 -*-
"""
Wiki & Knowledge Base Controller
Viveiro Análises - Comunidade de Conhecimento
"""

from wiki_helper import (
    slugify,
    render_markdown,
    extract_toc,
    estimate_reading_time,
    generate_excerpt,
    highlight_search_terms,
    can_read_page,
    can_edit_page,
)


def _get_user_name(user_id):
    """Helper to get user full name or email by id."""
    if not user_id:
        return "Comunidade"
    user_row = authdb.auth_user(user_id)
    if user_row:
        if user_row.first_name or user_row.last_name:
            return f"{user_row.first_name or ''} {user_row.last_name or ''}".strip()
        return user_row.email or f"Usuário #{user_id}"
    return f"Usuário #{user_id}"


def _get_user_initials(name):
    """Helper to get 2 initials from user name."""
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    elif len(parts) == 1 and parts[0]:
        return parts[0][:2].upper()
    return "KB"


def _get_all_tags_with_counts():
    """Returns a list of dicts with all unique tags and their count."""
    tag_counts = {}
    rows = authdb(authdb.wiki_page.id > 0).select(authdb.wiki_page.tags)
    for row in rows:
        if row.tags:
            tags = row.tags if isinstance(row.tags, list) else [t.strip() for t in str(row.tags).split(',') if t.strip()]
            for t in tags:
                t_clean = t.strip()
                if t_clean:
                    tag_counts[t_clean] = tag_counts.get(t_clean, 0) + 1
    return sorted([{"name": k, "count": v} for k, v in tag_counts.items()], key=lambda x: (-x["count"], x["name"]))


def index():
    """
    Main knowledge community portal.
    Displays search, statistics, featured topics, recent articles, and tag cloud.
    """
    # Fetch recent pages
    all_pages = authdb(authdb.wiki_page.id > 0).select(
        orderby=~authdb.wiki_page.modified_on | ~authdb.wiki_page.created_on,
        limitby=(0, 20)
    )

    # Filter by read permission
    user_groups = auth.user_groups.values() if auth.user else []
    visible_pages = []
    for p in all_pages:
        if can_read_page(p, auth.user, user_groups):
            author_name = _get_user_name(p.created_by)
            visible_pages.append({
                "id": p.id,
                "slug": p.slug,
                "title": p.title or p.slug,
                "excerpt": generate_excerpt(p.body, max_chars=160),
                "tags": p.tags if isinstance(p.tags, list) else [t.strip() for t in str(p.tags).split(',') if t.strip()],
                "author_name": author_name,
                "author_initials": _get_user_initials(author_name),
                "created_on": p.created_on,
                "modified_on": p.modified_on or p.created_on,
                "reading_time": estimate_reading_time(p.body),
            })

    # Stats
    total_articles = authdb(authdb.wiki_page.id > 0).count()
    all_tags = _get_all_tags_with_counts()
    total_tags = len(all_tags)
    
    # Contributors count
    contributors = authdb(authdb.wiki_page.id > 0).select(
        authdb.wiki_page.created_by, distinct=True)
    total_contributors = len(contributors)

    return dict(
        recent_pages=visible_pages,
        total_articles=total_articles,
        total_tags=total_tags,
        total_contributors=total_contributors,
        top_tags=all_tags[:12],
    )


# -----------------------------------------------------------------------------
# Article Reader
# -----------------------------------------------------------------------------
def view():
    """
    Displays an article with rich Markdown formatting, TOC, metadata,
    attachments gallery, and related articles.
    """
    slug_or_id = request.args(0) or "index"
    
    page = None
    if slug_or_id.isdigit():
        page = authdb.wiki_page(int(slug_or_id))
    else:
        page = authdb(authdb.wiki_page.slug == slug_or_id).select().first()

    if not page:
        if slug_or_id == "index":
            # If no index page exists yet, redirect to portal or offer creation
            if auth.user:
                session.flash = "A página inicial da Wiki ainda não foi criada. Crie o primeiro artigo!"
                redirect(URL('wiki', 'create', vars=dict(slug='index', title='Página Inicial')))
            else:
                redirect(URL('wiki', 'index'))
        else:
            session.flash = f"Artigo '{slug_or_id}' não encontrado."
            if auth.user:
                redirect(URL('wiki', 'create', vars=dict(slug=slugify(slug_or_id), title=slug_or_id.replace('-', ' ').title())))
            redirect(URL('wiki', 'index'))

    # Permission check
    user_groups = auth.user_groups.values() if auth.user else []
    if not can_read_page(page, auth.user, user_groups):
        session.flash = "Você não tem permissão para visualizar esta página restrita."
        redirect(URL('wiki', 'index'))

    # Render body
    rendered_html = render_markdown(page.body, page.render or "markdown")
    toc = extract_toc(rendered_html)
    reading_time = estimate_reading_time(page.body)
    author_name = _get_user_name(page.created_by)
    author_initials = _get_user_initials(author_name)
    user_can_edit = can_edit_page(page, auth.user, user_groups)

    # Attachments from wiki_media
    attachments = authdb(authdb.wiki_media.wiki_page == page.id).select(
        orderby=~authdb.wiki_media.created_on
    )

    # Related articles (sharing tags)
    related_articles = []
    page_tags = page.tags if isinstance(page.tags, list) else [t.strip() for t in str(page.tags).split(',') if t.strip()]
    if page_tags:
        # Search other pages containing any of these tags
        queries =  [authdb.wiki_page.tags.contains(t) for t in page_tags]
        query = queries[0]
        for q in queries[1:]:
            query = query | q
        matches = authdb((authdb.wiki_page.id != page.id) & query).select(limitby=(0, 5))
        for m in matches:
            if can_read_page(m, auth.user, user_groups):
                related_articles.append({
                    "slug": m.slug,
                    "title": m.title or m.slug,
                    "reading_time": estimate_reading_time(m.body),
                })

    return dict(
        page=page,
        rendered_html=rendered_html,
        toc=toc,
        reading_time=reading_time,
        author_name=author_name,
        author_initials=author_initials,
        user_can_edit=user_can_edit,
        attachments=attachments,
        related_articles=related_articles,
        tags=page_tags,
    )


# -----------------------------------------------------------------------------
# Create Article
# -----------------------------------------------------------------------------
@auth.requires_login()
def create():
    """
    Creates a new knowledge base article with title, slug, body, tags, and media.
    """
    user_groups = auth.user_groups.values() if auth.user else []
    
    pre_slug = request.vars.slug or ""
    pre_title = request.vars.title or ""

    if request.post_vars:
        title = (request.post_vars.title or "").strip()
        slug = (request.post_vars.slug or "").strip()
        body = (request.post_vars.body or "").strip()
        raw_tags = request.post_vars.tags or ""
        can_read = request.post_vars.getlist("can_read") if hasattr(request.post_vars, "getlist") else ["everybody"]
        can_edit = request.post_vars.getlist("can_edit") if hasattr(request.post_vars, "getlist") else ["everybody"]

        if not can_read:
            can_read = ["everybody"]
        if not can_edit:
            can_edit = ["everybody"]

        if not slug and title:
            slug = slugify(title)
        else:
            slug = slugify(slug)

        errors = []
        if not title:
            errors.append("O título do artigo é obrigatório.")
        if not slug:
            errors.append("O slug / endereço do artigo é obrigatório.")
        if not body:
            errors.append("O conteúdo do artigo não pode estar vazio.")

        # Check slug uniqueness
        if slug and authdb(authdb.wiki_page.slug == slug).count() > 0:
            errors.append(f"Já existe uma página com o slug '{slug}'. Por favor, escolha outro título ou slug.")

        if errors:
            response.flash = " ".join(errors)
        else:
            # Process tags
            if isinstance(raw_tags, str):
                tags_list = [t.strip() for t in raw_tags.split(',') if t.strip()]
            elif isinstance(raw_tags, list):
                tags_list = [t.strip() for t in raw_tags if t.strip()]
            else:
                tags_list = []

            # Insert wiki_page
            new_id = authdb.wiki_page.insert(
                slug=slug,
                title=title,
                body=body,
                tags=tags_list,
                can_read=can_read,
                can_edit=can_edit,
                render="markdown",
            )

            # Sync wiki_tag table
            for t in tags_list:
                authdb.wiki_tag.insert(name=t, wiki_page=new_id)

            # Check attachment upload
            if request.vars.attachment != "" and hasattr(request.vars.attachment, "file"):
                up_file = request.vars.attachment
                f_title = request.vars.attachment_title or up_file.filename
                authdb.wiki_media.insert(
                    wiki_page=new_id,
                    title=f_title,
                    filename=authdb.wiki_media.filename.store(up_file.file, up_file.filename),
                )

            session.flash = "Artigo publicado com sucesso na Base de Conhecimento!"
            redirect(URL('wiki', 'view', args=[slug]))

    all_tags = [t["name"] for t in _get_all_tags_with_counts()]
    return dict(
        pre_slug=pre_slug,
        pre_title=pre_title,
        all_tags=all_tags,
    )


# -----------------------------------------------------------------------------
# Edit Article
# -----------------------------------------------------------------------------
@auth.requires_login()
def edit():
    """
    Edits an existing article, managing body, tags, changelog, and media.
    """
    slug_or_id = request.args(0)
    if not slug_or_id:
        redirect(URL('wiki', 'index'))

    page = None
    if slug_or_id.isdigit():
        page = authdb.wiki_page(int(slug_or_id))
    else:
        page = authdb(authdb.wiki_page.slug == slug_or_id).select().first()

    if not page:
        session.flash = "Página não encontrada para edição."
        redirect(URL('wiki', 'index'))

    user_groups = auth.user_groups.values() if auth.user else []
    if not can_edit_page(page, auth.user, user_groups):
        session.flash = "Você não possui permissão para editar esta página."
        redirect(URL('wiki', 'view', args=[page.slug]))

    if request.post_vars:
        title = (request.post_vars.title or "").strip()
        body = (request.post_vars.body or "").strip()
        raw_tags = request.post_vars.tags or ""
        changelog = (request.post_vars.changelog or "").strip()
        can_read = request.post_vars.getlist("can_read") if hasattr(request.post_vars, "getlist") else (page.can_read or ["everybody"])
        can_edit = request.post_vars.getlist("can_edit") if hasattr(request.post_vars, "getlist") else (page.can_edit or ["everybody"])

        errors = []
        if not title:
            errors.append("O título não pode ser vazio.")
        if not body:
            errors.append("O conteúdo não pode ser vazio.")

        if errors:
            response.flash = " ".join(errors)
        else:
            # Process tags
            if isinstance(raw_tags, str):
                tags_list = [t.strip() for t in raw_tags.split(',') if t.strip()]
            elif isinstance(raw_tags, list):
                tags_list = [t.strip() for t in raw_tags if t.strip()]
            else:
                tags_list = []

            # Update page
            page.update_record(
                title=title,
                body=body,
                tags=tags_list,
                changelog=changelog,
                can_read=can_read,
                can_edit=can_edit,
            )

            # Sync tags
            authdb(authdb.wiki_tag.wiki_page == page.id).delete()
            for t in tags_list:
                authdb.wiki_tag.insert(name=t, wiki_page=page.id)

            # Handle attachment upload if submitted
            if request.vars.attachment != "" and hasattr(request.vars.attachment, "file"):
                up_file = request.vars.attachment
                f_title = request.vars.attachment_title or up_file.filename
                authdb.wiki_media.insert(
                    wiki_page=page.id,
                    title=f_title,
                    filename=authdb.wiki_media.filename.store(up_file.file, up_file.filename),
                )

            session.flash = "Artigo atualizado com sucesso!"
            redirect(URL('wiki', 'view', args=[page.slug]))

    attachments = authdb(authdb.wiki_media.wiki_page == page.id).select()
    all_tags = [t["name"] for t in _get_all_tags_with_counts()]
    tags_str = ", ".join(page.tags) if isinstance(page.tags, list) else (page.tags or "")

    return dict(
        page=page,
        attachments=attachments,
        all_tags=all_tags,
        tags_str=tags_str,
    )


# -----------------------------------------------------------------------------
# Delete Article
# -----------------------------------------------------------------------------
@auth.requires_login()
def delete():
    """
    Deletes an article along with its tags and media attachments.
    """
    slug_or_id = request.args(0)
    if not slug_or_id:
        redirect(URL('wiki', 'index'))

    page = None
    if slug_or_id.isdigit():
        page = authdb.wiki_page(int(slug_or_id))
    else:
        page = authdb(authdb.wiki_page.slug == slug_or_id).select().first()

    if not page:
        session.flash = "Artigo não encontrado."
        redirect(URL('wiki', 'index'))

    user_groups = auth.user_groups.values() if auth.user else []
    if not can_edit_page(page, auth.user, user_groups):
        session.flash = "Você não tem permissão para excluir este artigo."
        redirect(URL('wiki', 'view', args=[page.slug]))

    # Delete related records
    authdb(authdb.wiki_media.wiki_page == page.id).delete()
    authdb(authdb.wiki_tag.wiki_page == page.id).delete()
    authdb(authdb.wiki_page.id == page.id).delete()

    session.flash = f"Artigo '{page.title or page.slug}' foi excluído com sucesso."
    redirect(URL('wiki', 'index'))


# -----------------------------------------------------------------------------
# Search & Discovery
# -----------------------------------------------------------------------------
def search():
    """
    Search articles by query, tag, or author.
    Supports AJAX live suggestions and full search results page.
    """
    query_text = (request.vars.q or "").strip()
    tag_filter = (request.vars.tag or "").strip()

    user_groups = auth.user_groups.values() if auth.user else []
    
    results = []
    if query_text or tag_filter:
        conditions = []
        if query_text:
            conditions.append(authdb.wiki_page.title.contains(query_text) | authdb.wiki_page.body.contains(query_text) | authdb.wiki_page.tags.contains(query_text))
        if tag_filter:
            conditions.append(authdb.wiki_page.tags.contains(tag_filter))

        final_query = conditions[0]
        for c in conditions[1:]:
            final_query = final_query & c

        matches = authdb(final_query).select(orderby=~authdb.wiki_page.modified_on | ~authdb.wiki_page.created_on)
        for m in matches:
            if can_read_page(m, auth.user, user_groups):
                excerpt = generate_excerpt(m.body, max_chars=200)
                highlighted_title = highlight_search_terms(m.title or m.slug, query_text) if query_text else (m.title or m.slug)
                highlighted_excerpt = highlight_search_terms(excerpt, query_text) if query_text else excerpt
                
                results.append({
                    "id": m.id,
                    "slug": m.slug,
                    "title": m.title or m.slug,
                    "highlighted_title": highlighted_title,
                    "highlighted_excerpt": highlighted_excerpt,
                    "tags": m.tags if isinstance(m.tags, list) else [t.strip() for t in str(m.tags).split(',') if t.strip()],
                    "author_name": _get_user_name(m.created_by),
                    "modified_on": m.modified_on or m.created_on,
                    "reading_time": estimate_reading_time(m.body),
                })

    # AJAX Live Search
    if request.env.http_x_requested_with == "XMLHttpRequest" or request.vars.format == "json":
        import json
        response.headers["Content-Type"] = "application/json"
        return json.dumps([
            {
                "slug": r["slug"],
                "title": r["title"],
                "url": URL('wiki', 'view', args=[r["slug"]]),
                "tags": r["tags"],
                "reading_time": r["reading_time"]
            }
            for r in results[:8]
        ])

    all_tags = _get_all_tags_with_counts()
    return dict(
        query=query_text,
        tag_filter=tag_filter,
        results=results,
        all_tags=all_tags,
    )


# -----------------------------------------------------------------------------
# Tag Catalog
# -----------------------------------------------------------------------------
def tag():
    """
    Displays articles filtered by a specific tag/category.
    """
    tag_name = request.args(0) or request.vars.name or ""
    if not tag_name:
        redirect(URL('wiki', 'index'))

    user_groups = auth.user_groups.values() if auth.user else []
    matches = authdb(authdb.wiki_page.tags.contains(tag_name)).select(
        orderby=~authdb.wiki_page.modified_on | ~authdb.wiki_page.created_on
    )

    articles = []
    for m in matches:
        if can_read_page(m, auth.user, user_groups):
            author_name = _get_user_name(m.created_by)
            articles.append({
                "slug": m.slug,
                "title": m.title or m.slug,
                "excerpt": generate_excerpt(m.body, max_chars=160),
                "tags": m.tags if isinstance(m.tags, list) else [t.strip() for t in str(m.tags).split(',') if t.strip()],
                "author_name": author_name,
                "author_initials": _get_user_initials(author_name),
                "modified_on": m.modified_on or m.created_on,
                "reading_time": estimate_reading_time(m.body),
            })

    all_tags = _get_all_tags_with_counts()
    return dict(
        tag_name=tag_name,
        articles=articles,
        all_tags=all_tags,
    )


# -----------------------------------------------------------------------------
# Pages Directory
# -----------------------------------------------------------------------------
def pages():
    """
    Comprehensive directory/table of all knowledge base articles.
    """
    user_groups = auth.user_groups.values() if auth.user else []
    all_rows = authdb(authdb.wiki_page.id > 0).select(
        orderby=authdb.wiki_page.title | authdb.wiki_page.slug
    )

    page_list = []
    for p in all_rows:
        if can_read_page(p, auth.user, user_groups):
            page_list.append({
                "id": p.id,
                "slug": p.slug,
                "title": p.title or p.slug,
                "tags": p.tags if isinstance(p.tags, list) else [t.strip() for t in str(p.tags).split(',') if t.strip()],
                "author_name": _get_user_name(p.created_by),
                "created_on": p.created_on,
                "modified_on": p.modified_on or p.created_on,
                "can_edit": can_edit_page(p, auth.user, user_groups),
            })

    return dict(
        pages=page_list,
        total=len(page_list),
    )


# -----------------------------------------------------------------------------
# Media Attachment Handlers
# -----------------------------------------------------------------------------
@auth.requires_login()
def media_delete():
    """
    Deletes an attachment record from wiki_media.
    """
    media_id = request.args(0)
    if not media_id:
        redirect(URL('wiki', 'index'))

    media = authdb.wiki_media(media_id)
    if not media:
        session.flash = "Arquivo não encontrado."
        redirect(URL('wiki', 'index'))

    page = authdb.wiki_page(media.wiki_page)
    user_groups = auth.user_groups.values() if auth.user else []
    if page and not can_edit_page(page, auth.user, user_groups):
        session.flash = "Você não tem permissão para remover anexos deste artigo."
        redirect(URL('wiki', 'view', args=[page.slug]))

    authdb(authdb.wiki_media.id == media_id).delete()
    session.flash = "Anexo removido com sucesso."
    
    if page:
        redirect(URL('wiki', 'edit', args=[page.slug]))
    redirect(URL('wiki', 'index'))


# -----------------------------------------------------------------------------
# Live Markdown Preview AJAX Endpoint
# -----------------------------------------------------------------------------
def preview():
    """
    AJAX endpoint for real-time markdown preview during editing.
    """
    raw_body = request.vars.body or ""
    render_type = request.vars.render_type or "markdown"
    html = render_markdown(raw_body, render_type)
    return html


# -----------------------------------------------------------------------------
# Navigation Menu Actions
# -----------------------------------------------------------------------------
def base_de_conhecimento(): #Menu
    redirect(URL('wiki', 'index'))


def novo_artigo(): #Menu
    redirect(URL('wiki', 'create'))


def todos_os_artigos(): #Menu
    redirect(URL('wiki', 'pages'))

