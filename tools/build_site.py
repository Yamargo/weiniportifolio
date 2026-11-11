"""Generates index.html + i18n/*.json from a single content model.

Every user-facing string is registered once with S(key, pt) and gets its EN/ZH
counterparts from the translation tables, so a missing translation fails the build.
"""
import json, sys, html
sys.path.insert(0, '/tmp/i18n')
import data as D

SITE = '/home/claude/proj/site'
A = json.load(open('/home/claude/proj/assets.json'))

# ------------------------------------------------------------------ strings
LK = {pt: (en, zh) for pt, en, zh in D.ITEMS}
STR = {}      # key -> {pt,en,zh}


def S(key, pt, en=None, zh=None):
    if (en is None or zh is None) and key in STR and STR[key]['pt'] == pt:
        return pt
    if en is None or zh is None:
        if pt not in LK:
            raise KeyError(f'missing translation for {key!r}: {pt[:50]}')
        en, zh = LK[pt]
    assert key not in STR or STR[key]['pt'] == pt, f'dup key {key}'
    STR[key] = {'pt': pt, 'en': en, 'zh': zh}
    return pt


def esc(s):
    return html.escape(s, quote=True)


def T(key, pt, en=None, zh=None, tag=None):
    """text node content bound to a key (plain text)"""
    S(key, pt, en, zh)
    return f'data-i18n="{key}"', pt


def txt(key, pt, en=None, zh=None):
    S(key, pt, en, zh)
    return f'<span data-i18n="{key}">{esc(pt)}</span>'


def el(tag, key, pt, en=None, zh=None, cls=None, rich=False, attrs=''):
    S(key, pt, en, zh)
    c = f' class="{cls}"' if cls else ''
    attr = 'data-i18n-html' if rich else 'data-i18n'
    body = pt if rich else esc(pt)
    return f'<{tag}{c} {attr}="{key}"{(" " + attrs) if attrs else ""}>{body}</{tag}>'


def alt(key, pt, en=None, zh=None):
    S(key, pt, en, zh)
    return f'alt="{esc(pt)}" data-i18n-alt="{key}"'


# ------------------------------------------------------------------ shared UI strings
S('meta.description',
  'Portfólio de Vinícius Flórido Marques Costa: atendimento ao cliente, suporte de TI, liderança de Service Desk, design gráfico e SEO, com experiência em Laos, Albânia, Camboja, Armênia e Filipinas.',
  'Portfolio of Vinícius Flórido Marques Costa: customer service, IT support, Service Desk leadership, graphic design and SEO, with experience in Laos, Albania, Cambodia, Armenia and the Philippines.',
  'Vinícius Flórido Marques Costa 的作品集：客户服务、IT 支持、服务台团队管理、平面设计和 SEO，工作经历遍及老挝、阿尔巴尼亚、柬埔寨、亚美尼亚和菲律宾。')
S('ui.skip', 'Ir para o conteúdo principal', 'Skip to main content', '跳到主要内容')
S('ui.nav', 'Navegação principal', 'Main navigation', '主导航')
S('ui.lang', 'Idioma', 'Language', '语言')
S('ui.announce', 'Página carregada', 'Page loaded', '页面已加载')
S('ui.close', 'Fechar', 'Close', '关闭')
S('ui.prev', 'Anterior', 'Previous', '上一张')
S('ui.next', 'Próxima', 'Next', '下一张')
S('ui.zoom', 'Ampliar imagem', 'Enlarge image', '放大图片')
S('ui.video', 'Faixa decorativa animada de moedas', 'Decorative animated coin strip', '装饰性金币动画条')

PAGES = ['home', 'laos', 'albania', 'cambodia', 'armenia', 'philippines']
for k, (pt, en, zh) in {'home': ('Início', 'Home', '首页'),
                        'laos': ('Laos', 'Laos', '老挝'),
                        'albania': ('Albânia', 'Albania', '阿尔巴尼亚'),
                        'cambodia': ('Camboja', 'Cambodia', '柬埔寨'),
                        'armenia': ('Armênia', 'Armenia', '亚美尼亚'),
                        'philippines': ('Filipinas', 'Philippines', '菲律宾')}.items():
    S(f'country.{k}', pt, en, zh)
SITE_NAME = 'Vinícius Flórido'
FLAG = {'laos': 'la', 'albania': 'al', 'cambodia': 'kh', 'armenia': 'am', 'philippines': 'ph'}
NAVIMG = {'home': 'home', 'laos': 'la', 'albania': 'al', 'cambodia': 'kh', 'armenia': 'am', 'philippines': 'ph'}


def flag(code, w=28, cls='flag'):
    return f'<img class="{cls}" src="assets/flags/{code}.svg" alt="" width="{w}" height="{round(w*3/4)}" decoding="async">'


def navimg(k, h=30, cls='cn'):
    w, hh = A['nav-' + NAVIMG[k]]
    return (f'<img class="{cls}" src="assets/img/nav/{NAVIMG[k]}.webp" width="{w}" height="{hh}" '
            f'{alt("country." + k, *[STR["country." + k][x] for x in ("pt", "en", "zh")])} decoding="async">')


# ------------------------------------------------------------------ components
ICON = {
    'megaphone': '<path d="M3 11v2a1 1 0 0 0 1 1h2l5 4V6L6 10H4a1 1 0 0 0-1 1Zm13.5 1a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4Zm2.5 0a7 7 0 0 1-4.5 6.5v-2a5 5 0 0 0 0-9v-2A7 7 0 0 1 19 12Z"/>',
    'github': '<path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.2-3.4-1.2-.5-1.1-1.1-1.4-1.1-1.4-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.4 1.1 2.9.8.1-.7.4-1.1.6-1.4-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2 1-2.7-.1-.3-.4-1.300.1-2.700 0 0 .8-.3 2.800 1a9.600 9.600 0 0 1 5 0c1.900-1.300 2.800-1 2.800-1 .5 1.400.2 2.400.1 2.700.6.700 1 1.600 1 2.700 0 3.900-2.400 4.700-4.600 5 .4.300.7.900.7 1.800v2.700c0 .3.2.600.7.500A10 10 0 0 0 12 2Z"/>',
}


def icon(name):
    return f'<svg class="ico" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="currentColor">{ICON[name]}</svg>'


def srcset(info, sizes):
    ts = info['thumbs']
    ss = ', '.join(f'{p} {w}w' for w, h, p in ts)
    mid = ts[len(ts) // 2] if len(ts) > 2 else ts[0]
    return f'src="{mid[2]}" srcset="{ss}" sizes="{sizes}" width="{info["w"]}" height="{info["h"]}"'


SIZES_SHOT = '(min-width: 1000px) 300px, (min-width: 600px) 45vw, 92vw'
SIZES_SQ = '(min-width: 1000px) 230px, (min-width: 600px) 30vw, 46vw'


def shot(key, info, title_pt, desc_pt, gallery, square=False, desc_key=None, desc_vals=None):
    full = info['full']
    S(f'{key}.title', title_pt)
    if desc_vals:
        S(f'{key}.desc', desc_pt, *desc_vals)
    else:
        S(f'{key}.desc', desc_pt)
    t = STR[f'{key}.title']
    cls = 'shot sq reveal' if square else 'shot reveal'
    return f'''<figure class="{cls}">
<button type="button" class="shot-btn" data-lightbox="{gallery}" data-full="{full[2]}" data-w="{full[0]}" data-h="{full[1]}" data-i18n-aria="ui.zoom" aria-label="Ampliar imagem">
<img {srcset(info, SIZES_SQ if square else SIZES_SHOT)} {alt(f"{key}.title", t["pt"], t["en"], t["zh"])} loading="lazy" decoding="async"></button>
<figcaption><b data-i18n="{key}.title">{esc(title_pt)}</b><span data-i18n="{key}.desc">{esc(desc_pt)}</span></figcaption>
</figure>'''


def card(key, title_pt, body_pt, extra='', ico='', title_tag='h3', titles=None):
    return f'''<article class="card reveal">{ico}{el(title_tag, key + ".title", title_pt, cls="card-title")}{el("p", key + ".body", body_pt)}{extra}</article>'''


def linkcard(key, ico, title_pt, body_pt, href, cta_pt, primary=False):
    S(f'{key}.cta', cta_pt)
    cls = 'btn btn-primary' if primary else 'btn btn-link'
    return f'''<article class="card reveal">
<div class="card-ico">{ico}</div>{el("h3", key + ".title", title_pt, cls="card-title")}{el("p", key + ".body", body_pt)}
<a class="{cls}" href="{href}" target="_blank" rel="noopener noreferrer"><span data-i18n="{key}.cta">{esc(cta_pt)}</span></a>
</article>'''


def explain(key, h3_pt, h3_en, h3_zh, body_pt, body_en, body_zh):
    S(f'{key}.title', h3_pt, h3_en, h3_zh)
    S(f'{key}.body', body_pt, body_en, body_zh)
    return f'''<aside class="explain reveal"><h3 data-i18n="{key}.title">{esc(h3_pt)}</h3><div data-i18n-html="{key}.body">{body_pt}</div></aside>'''


FACT_LABEL = {'company': ('Empresa', 'Company', '公司'), 'period': ('Período', 'Period', '任职时间'),
              'role': ('Cargo', 'Role', '职位'), 'place': ('Local', 'Location', '地点')}
for k, v in FACT_LABEL.items():
    S(f'fact.{k}', *v)


def facts(items):
    out = []
    for k, vkey, pt, en, zh in items:
        if vkey:
            S(vkey, pt, en, zh)
            val = f'<dd data-i18n="{vkey}">{esc(pt)}</dd>'
        else:
            val = f'<dd>{esc(pt)}</dd>'
        out.append(f'<div><dt data-i18n="fact.{k}">{FACT_LABEL[k][0]}</dt>{val}</div>')
    return '<dl class="facts reveal">' + ''.join(out) + '</dl>'


def hero(page, p_pt):
    return f'''<header class="hero">
<h1 tabindex="-1">{flag(FLAG[page], 44, "flag flag-lg")}<span data-i18n="country.{page}">{esc(STR["country." + page]["pt"])}</span></h1>
{el("p", f"{page}.lede", p_pt)}
</header>'''


def section(sid, h2key, h2pt, subpt=None, subkey=None, body='', h2vals=None):
    S(h2key, h2pt, *(h2vals or ())) if h2vals else S(h2key, h2pt)
    sub = el('p', subkey, subpt, cls='sub') if subpt else ''
    return f'''<section class="section" aria-labelledby="{sid}-h">
<h2 id="{sid}-h" data-i18n="{h2key}">{esc(h2pt)}</h2>{sub}
{body}
</section>'''


# ------------------------------------------------------------------ pages
def home():
    intro_pt = ('Sou o <b>Vinícius Flórido Marques Costa</b>, brasileiro, com experiência internacional em <b>atendimento ao cliente</b>, '
                '<b>suporte de TI</b> e <b>liderança de equipes de Service Desk</b>. Já trabalhei nas Filipinas, em Portugal, na Albânia, em Laos '
                'e no Camboja, e em home office para a Armênia e o Paquistão. Também tenho experiência com <b>design gráfico</b> e <b>tráfego pago</b>.<br>\n'
                'Idiomas: português, inglês e espanhol (fluentes), e chinês com apoio de ferramentas de IA. Escolha um país abaixo para ver o que fiz em cada lugar.')
    S('home.intro.title', '👋 Apresentação'.replace('👋 ', ''), D.APRES[0].replace('👋 ', ''), D.APRES[1].replace('👋 ', ''))
    S('home.intro.body', intro_pt, D.INTRO[0], D.INTRO[1])
    tags = ['Atendimento ao cliente', 'Suporte de TI', 'Liderança de Service Desk', 'Design gráfico', 'Tráfego pago (Meta Ads)', 'Automação de marketing']
    tag_html = ''
    for i, t in enumerate(tags):
        S(f'home.skill.{i}', t)
        tag_html += f'<li data-i18n="home.skill.{i}">{esc(t)}</li>'
    cards = ''
    desc = {'laos': 'BoomRio e 66game: páginas de SEO, links e screenshots.',
            'albania': 'Design gráfico, banners e fotos da estadia.',
            'cambodia': 'Atendimento ao cliente, segurança de contas e análise de saques.',
            'armenia': 'Service Desk em home office, no Brasil e nas plataformas do Paquistão.',
            'philippines': 'Análise de qualidade, design gráfico e suporte de TI em Manila.'}
    for k in ['laos', 'albania', 'cambodia', 'armenia', 'philippines']:
        cards += f'''<a class="card homecard reveal" href="#{k}">{flag(FLAG[k], 64, "flag flag-xl")}<h3>{navimg(k, 56, "cn cn-lg")}</h3>{el("p", f"home.card.{k}", desc[k])}</a>'''
    w, h = A['hero']
    S('home.hero.alt', 'Banner do portfólio com ilustração de um tigre da fortuna',
      'Portfolio banner with a fortune tiger illustration', '带有财富之虎插画的作品集横幅')
    return f'''<div class="herobanner"><h1 class="sr-only" tabindex="-1" data-i18n="home.h1">{esc(S("home.h1", "Vinícius Flórido Marques Costa — Portfólio", "Vinícius Flórido Marques Costa — Portfolio", "Vinícius Flórido Marques Costa — 作品集"))}</h1>
<img class="hb-one" src="assets/img/ui/hero.webp" width="{w}" height="{h}" {alt("home.hero.alt", *STR["home.hero.alt"].values())} fetchpriority="high" decoding="async"></div>
<section class="section" aria-labelledby="intro-h"><div class="explain reveal"><h2 id="intro-h" class="explain-title" data-i18n="home.intro.title">{esc(STR["home.intro.title"]["pt"])}</h2>
<p data-i18n-html="home.intro.body">{intro_pt}</p>
<ul class="tags" role="list">{tag_html}</ul></div></section>
<section class="section" aria-label="{esc(S("home.countries", "Países", "Countries", "国家"))}" data-i18n-aria="home.countries"><div class="grid">{cards}</div></section>'''


def laos():
    S('laos.lede', 'BoomRio e 66game: páginas de SEO, links e capturas de tela. Esta página será atualizada conforme novos materiais forem enviados.')
    links = (
        linkcard('laos.tg', icon('megaphone'), 'Canal BoomRio · Telegram', 'Canal oficial com jogos, bônus, informativos e promoções.', 'https://t.me/+j5zQhgkIkEhjNGRk', 'Abrir canal ↗')
        + linkcard('laos.g66', flag('in', 36, 'flag flag-md'), 'Página SEO · 66game',
                   'Site de divulgação da plataforma indiana da mesma empresa da BoomRio, com guia de download, FAQ e avaliações.', 'https://66gameblog.com', 'Abrir site ↗')
        + linkcard('laos.gh', icon('github'), 'GitHub · BoomRio e Game66', 'Repositórios das páginas de SEO da BoomRio e do 66game.',
                   'https://github.com/boomrioseo-dev?tab=repositories', 'Ver repositórios ↗', primary=True))
    g = 'seo'
    shots = [
        shot('laos.s1', A['seo-planning'], 'Planejamento de nova plataforma', 'Conversa de equipe sobre limites de envio e ideias de nomes para uma nova plataforma.', g),
        shot('laos.s2', A['seo-team'], 'Grupo BOOM TEAM', 'Grupo de promoção com relatório de desempenho e orientações para a equipe.', g),
        shot('laos.s3', A['seo-channel'], 'Canal oficial BoomRio', 'Canal com 3.702 inscritos e publicação com códigos de resgate.', g),
        shot('laos.s4', A['seo-archive'], 'Conversas arquivadas', 'Lista de contatos e conversa sobre dias trabalhados e pagamento.', g),
        shot('laos.s5', A['seo-google'], 'Primeiro lugar no Google', 'Busca por “boomrio”: uma das páginas de SEO aparece em primeiro lugar nos resultados.', g),
        shot('laos.s6', A['seo-instagram'], 'Arte para Instagram', 'Story criado para a BoomRio, convidando pessoas a se tornarem agentes.', g),
        shot('laos.s7', A['seo-telegram-vip'], 'Grupo VIP no Telegram', 'Mensagem fixada com código de resgate e regras de bônus.', g),
    ]
    S('laos.s8.title', 'Vídeo promocional'); S('laos.s8.desc', 'Animação curta de 5 segundos criada para divulgação.')
    video = f'''<figure class="shot shot-video reveal"><video controls playsinline preload="none" poster="assets/video/promo-poster.webp" width="540" height="960" data-i18n-aria="laos.s8.title" aria-label="Vídeo promocional"><source src="assets/video/promo.mp4" type="video/mp4"></video>
<figcaption><b data-i18n="laos.s8.title">Vídeo promocional</b><span data-i18n="laos.s8.desc">Animação curta de 5 segundos criada para divulgação.</span></figcaption></figure>'''
    shots.append(video)
    shots.append(shot('laos.s9', A['seo-github'], 'Perfil no GitHub', 'Conta boomrioseo-dev com 45 repositórios e 341 contribuições no último ano.', g))
    S('laos.group', 'SEO · BOOM', 'SEO · BOOM', 'SEO · BOOM')
    body2 = f'<h3 class="grp" data-i18n="laos.group">SEO · BOOM</h3><div class="grid grid-shots">{"".join(shots)}</div>'
    f = facts([('company', None, 'STAR COMPANY', '', ''),
               ('role', 'role.csa', 'Analista de Atendimento ao Cliente', 'Customer Service Analyst', '客户服务分析员'),
               ('period', 'period.khlaos', 'Jun 2025 – Fev 2026', 'Jun 2025 – Feb 2026', '2025年6月 – 2026年2月'),
               ('place', 'place.laos', 'Triângulo Dourado (Laos)', 'Golden Triangle (Laos)', '老挝金三角')])
    ex = explain('laos.time', 'Sobre a minha passagem', D.PASS_H3[0].replace('📍 ', ''), D.PASS_H3[1].replace('📍 ', ''),
                 'Trabalhei como <b>Analista de Atendimento ao Cliente</b> na STAR COMPANY, começando no Triângulo Dourado, em Laos, e depois fui transferido para o Camboja. Esta página reúne os materiais da BoomRio e do 66game: páginas de SEO, links e capturas de tela.',
                 'I worked as a <b>Customer Service Analyst</b> at STAR COMPANY, starting in the Golden Triangle, in Laos, and was later transferred to Cambodia. This page gathers the BoomRio and 66game material: SEO pages, links and screenshots.',
                 '我在 STAR COMPANY 担任<b>客户服务分析员</b>，起初在老挝的金三角地区工作，之后调往柬埔寨。本页汇集了 BoomRio 与 66game 的资料：SEO 页面、链接和截图。')
    return (hero('laos', STR['laos.lede']['pt']) + f'<div class="section">{f}{ex}</div>'
            + section('projects', 'laos.projects.title', 'BoomRio e 66game', 'Páginas de SEO, canal no Telegram e repositórios', 'laos.projects.sub', f'<div class="grid">{links}</div>')
            + section('screens', 'laos.screens.title', 'Screenshots', 'Capturas de tela dos trabalhos', 'laos.screens.sub', body2))


def albania():
    S('albania.lede', 'Trabalhos de design gráfico e registros da estadia no local.')
    h3 = D.EXPL['🎨 Sobre o trabalho']
    ex = explain('albania.about', 'Sobre o trabalho', h3[0].replace('🎨 ', ''), h3[1].replace('🎨 ', ''),
                 'Na Albânia realizei trabalhos de design gráfico, como banners para SEO, para Instagram e outros materiais de divulgação, além de fotografias da estadia no local. Abaixo estão os banners, organizados por plataforma, e os registros do período.',
                 h3[2], h3[3])
    groups = [('J6.Game', [('rooster', 'Galo e ninho'), ('jungle', 'Selva e lêmures'), ('waterfall', 'Cachoeira e arara')]),
              ('Z9.Game', [('pirate', 'Tema pirata'), ('leprechaun', 'Duende e pote de ouro'), ('western', 'Tema faroeste'), ('fortune-god', 'Tigre e deus da fortuna'), ('floating-market', 'Mercado flutuante')]),
              ('T9.Game', [('tiger-mouse', 'Tigre e rato'), ('penguin', 'Pinguim no gelo'), ('ganesha', 'Ganesha dourado'), ('piglet', 'Porquinho dourado'), ('dragon', 'Dragão')])]
    S('albania.banner.desc', 'Banner de divulgação.')
    body = ''
    for gname, items in groups:
        cells = ''
        for slug, title in items:
            info = A['b-' + slug]
            full = info['full']
            S(f'albania.{slug}', title)
            t = STR[f'albania.{slug}']
            cells += f'''<figure class="shot sq reveal"><button type="button" class="shot-btn" data-lightbox="banners" data-full="{full[2]}" data-w="{full[0]}" data-h="{full[1]}" data-i18n-aria="ui.zoom" aria-label="Ampliar imagem"><img {srcset(info, SIZES_SQ)} alt="{gname} — {esc(title)}" loading="lazy" decoding="async"></button>
<figcaption><b data-i18n="albania.{slug}">{esc(title)}</b><span data-i18n="albania.banner.desc">Banner de divulgação.</span></figcaption></figure>'''
        body += f'<h3 class="grp">{gname}</h3><div class="grid grid-banners">{cells}</div>'
    stay = shot('albania.stay', A['stay'], 'Estação de trabalho', 'Registro fotográfico da estadia.', 'stay')
    f = facts([('company', None, 'BRILLIANT ENTERTAINMENT', '', ''),
               ('role', 'role.itpt', 'Analista de TI e Tráfego Pago', 'IT and Paid Traffic Analyst', 'IT 与付费流量分析员'),
               ('period', 'period.al', 'Out 2024 – Mai 2025', 'Oct 2024 – May 2025', '2024年10月 – 2025年5月'),
               ('place', 'place.al', 'Albânia', 'Albania', '阿尔巴尼亚')])
    ex0 = explain('albania.time', 'Sobre a minha passagem', D.PASS_H3[0].replace('📍 ', ''), D.PASS_H3[1].replace('📍 ', ''),
                  'Trabalhei como <b>Analista de TI e Tráfego Pago</b> na BRILLIANT ENTERTAINMENT, na Albânia, de outubro de 2024 a maio de 2025. Além do design gráfico, atuei com tráfego pago (Meta Ads), automação de marketing e suporte de TI.',
                  'I worked as an <b>IT and Paid Traffic Analyst</b> at BRILLIANT ENTERTAINMENT, in Albania, from October 2024 to May 2025. Besides graphic design, I worked on paid traffic (Meta Ads), marketing automation and IT support.',
                  '2024 年 10 月至 2025 年 5 月，我在阿尔巴尼亚的 BRILLIANT ENTERTAINMENT 担任 <b>IT 与付费流量分析员</b>。除平面设计外，我还负责付费流量（Meta Ads）、营销自动化和 IT 支持。')
    return (hero('albania', STR['albania.lede']['pt']) + f'<div class="section">{f}{ex0}{ex}</div>'
            + section('banners', 'albania.banners.title', 'Banners e artes de divulgação', body=body)
            + section('photos', 'albania.photos.title', 'Fotos da estadia', 'Registros do período no local', 'albania.photos.sub', f'<div class="grid grid-shots">{stay}</div>'))


def role_cards(prefix, items):
    return ''.join(card(f'{prefix}.{i}', t, b) for i, (t, b) in enumerate(items))


def cambodia():
    S('cambodia.lede', 'O que eu fiz no Camboja: atendimento ao cliente e análise de saques.')
    pt_pass = 'Trabalhei como <b>Analista de Atendimento ao Cliente</b> na STAR COMPANY de junho de 2025 a fevereiro de 2026. Comecei no Triângulo Dourado, em Laos, e depois fui transferido para o Camboja.'
    en, zh = D.PASS['STAR COMPANY']
    ex = explain('cambodia.about', 'Sobre a minha passagem', D.PASS_H3[0].replace('📍 ', ''), D.PASS_H3[1].replace('📍 ', ''), pt_pass, en, zh)
    f = facts([('company', None, 'STAR COMPANY', '', ''),
               ('role', 'role.csa', 'Analista de Atendimento ao Cliente', 'Customer Service Analyst', '客户服务分析员'),
               ('period', 'period.khlaos', 'Jun 2025 – Fev 2026', 'Jun 2025 – Feb 2026', '2025年6月 – 2026年2月'),
               ('place', 'place.khlaos', 'Triângulo Dourado (Laos) e Camboja', 'Golden Triangle (Laos) and Cambodia', '老挝金三角和柬埔寨')])
    cs = role_cards('cambodia.r', [
        ('Segurança de contas', 'Redefinia senhas de login e de saque, garantindo a segurança da conta e um acesso eficiente.'),
        ('Análise de saques', 'Analisava o status das solicitações de saque, identificava os motivos de aprovação ou falha e explicava o resultado ao cliente com clareza.'),
        ('Suporte ao cliente', 'Dava suporte sobre contas e transações financeiras e avisava os usuários sobre atualizações de bônus e mudanças nas funções da plataforma.')])
    return (hero('cambodia', STR['cambodia.lede']['pt']) + f'<div class="section">{f}{ex}</div>'
            + section('duties', 'cambodia.duties.title', 'O que eu fazia', 'Principais responsabilidades', 'cambodia.duties.sub', f'<div class="grid">{cs}</div>'))


def armenia():
    S('armenia.lede', 'Trabalho remoto (home office) como Supervisor de Service Desk, na operação do Brasil e nas plataformas do Paquistão.')
    e = D.EXPL
    ex1 = explain('armenia.home', 'Serviço em home office', e['🏠 Serviço em home office'][0].replace('🏠 ', ''), e['🏠 Serviço em home office'][1].replace('🏠 ', ''),
                  'Na Armênia trabalhei em <b>home office</b> como <b>Supervisor de Service Desk</b> na A61.COM, na operação do Brasil, de junho a outubro de 2026.',
                  e['🏠 Serviço em home office'][2], e['🏠 Serviço em home office'][3])
    ex2 = explain('armenia.shift', 'Mudança de operação', e['🔄 Mudança de operação'][0].replace('🔄 ', ''), e['🔄 Mudança de operação'][1].replace('🔄 ', ''),
                  'Com o encerramento da operação da A61.COM no Brasil por restrições regulatórias, passei para as <b>plataformas do Paquistão (sites 8557 e 7987)</b>, também em <b>home office</b>.',
                  e['🔄 Mudança de operação'][2], e['🔄 Mudança de operação'][3])
    ex3 = explain('armenia.wd', 'Time de saques', e['💸 Time de saques'][0].replace('💸 ', ''), e['💸 Time de saques'][1].replace('💸 ', ''),
                  'Assumi temporariamente a gestão da equipe de saques.<ul><li><b>Cargo:</b> líder temporário da equipe de saques, a partir de 09/10/2026.</li><li><b>Escopo:</b> gestão da equipe de saques das plataformas do Paquistão, sites 8557 e 7987.</li><li><b>Resultado:</b> com a chegada do líder efetivo de saques, fui promovido a Coordenador de Service Desk.</li></ul>',
                  e['💸 Time de saques'][2], e['💸 Time de saques'][3])
    ex4 = explain('armenia.sites', 'O que fiz pelos sites 8557 e 7987', e['🧭 O que fiz pelos sites 8557 e 7987'][0].replace('🧭 ', ''), e['🧭 O que fiz pelos sites 8557 e 7987'][1].replace('🧭 ', ''),
                  '<ul><li>Coordenação do Service Desk dos dois sites.</li><li>Escalas de trabalho e planejamento de férias das equipes.</li><li>Entrevistas de recrutamento.</li><li>Fluxos de atendimento conforme as regras da plataforma.</li><li>Ponte de comunicação entre a gestão chinesa e os funcionários.</li><li>Resposta a perguntas gerais sobre o mercado.</li></ul>',
                  e['🧭 O que fiz pelos sites 8557 e 7987'][2], e['🧭 O que fiz pelos sites 8557 e 7987'][3])
    f = facts([('company', None, 'A61.COM', '', ''),
               ('role', 'role.sds', 'Supervisor de Service Desk', 'Service Desk Supervisor', '服务台主管'),
               ('period', 'period.am', 'Jun – Out 2026', 'Jun – Oct 2026', '2026年6月 – 10月'),
               ('place', 'place.remote', 'Home office (remoto)', 'Remote (home office)', '居家办公（远程）')])
    brazil = role_cards('armenia.br', [
        ('Escalas e férias', 'Montava as escalas de trabalho e o planejamento de férias da equipe.'),
        ('Recrutamento', 'Conduzia as entrevistas de recrutamento.'),
        ('Fluxos de atendimento', 'Criava os fluxos de serviço segundo as regras da plataforma e facilitava a comunicação entre a gestão chinesa e a equipe brasileira.'),
        ('Dúvidas sobre o mercado', 'Respondia perguntas gerais sobre o mercado brasileiro.')])
    pk = ''.join([
        card('armenia.pk.0', 'Coordenação de Service Desk', 'Coordeno o Service Desk dos sites 8557 e 7987, com escalas de trabalho, férias e entrevistas de recrutamento.'),
        card('armenia.pk.1', 'Equipe de saques', 'A partir de 09/10/2026, liderei temporariamente a equipe de saques das duas plataformas. Com a chegada do líder efetivo, fui promovido a Coordenador de Service Desk.'),
        card('armenia.pk.2', 'Fluxos e comunicação', 'Defino os fluxos de atendimento conforme as regras da plataforma e facilito a comunicação entre a gestão chinesa e os funcionários.'),
        card('armenia.pk.3', 'Dúvidas sobre o mercado', 'Respondo perguntas gerais sobre o mercado.')])
    return (hero('armenia', STR['armenia.lede']['pt']) + f'<div class="section">{f}<div class="explain-grid">{ex1}{ex2}</div></div>'
            + section('brazil', 'armenia.br.title', 'O que eu fazia', 'Principais responsabilidades', 'armenia.br.sub', f'<div class="grid">{brazil}</div>')
            + section('pakistan', 'armenia.pk.title', 'A61.COM · sites 8557 e 7987, também em home office', body=f'<div class="grid">{pk}</div><div class="explain-grid">{ex3}{ex4}</div>') + docs_section())


def philippines():
    S('philippines.lede', 'O que eu fiz em Manila: qualidade, design gráfico e suporte de TI.')
    pt_pass = 'Trabalhei como <b>Analista Bilíngue</b> na PS SERVICES, em Manila, de agosto de 2023 a outubro de 2024. Nesse período atuei em três áreas: análise de qualidade e tradução, design gráfico e TI.'
    en, zh = D.PASS['PS SERVICES']
    ex = explain('philippines.about', 'Sobre a minha passagem', D.PASS_H3[0].replace('📍 ', ''), D.PASS_H3[1].replace('📍 ', ''), pt_pass, en, zh)
    f = facts([('company', None, 'PS SERVICES', '', ''),
               ('role', 'role.bil', 'Analista Bilíngue', 'Bilingual Analyst', '双语分析员'),
               ('period', 'period.ph', 'Ago 2023 – Out 2024', 'Aug 2023 – Oct 2024', '2023年8月 – 2024年10月'),
               ('place', 'place.manila', 'Manila', 'Manila', '马尼拉')])
    cs = role_cards('philippines.r', [
        ('Análise de qualidade e tradução', 'Durante 3 meses, avaliei conversas de atendimento para melhorar a qualidade e a eficiência e apliquei treinamentos semanais para elevar o desempenho da equipe.'),
        ('Treinamento de idiomas', 'Dei treinamento de português aos funcionários e de inglês aos colegas filipinos.'),
        ('Design gráfico', 'Durante 6 meses, produzi banners, logotipos e outros conteúdos gráficos junto com os desenvolvedores e a equipe de SEO.'),
        ('TI', 'Durante 6 meses, subi páginas de sites em sistemas Linux, configurei roteadores e dei suporte diário de VPN e a usuários.')])
    return (hero('philippines', STR['philippines.lede']['pt']) + f'<div class="section">{f}{ex}</div>'
            + section('duties', 'philippines.duties.title', 'O que eu fazia', 'Principais responsabilidades', 'philippines.duties.sub', f'<div class="grid">{cs}</div>'))


def doclink(key, fmt, href, title, body, cta):
    S(f'{key}.title', *title); S(f'{key}.body', *body)
    S('docs.open', *cta)
    return f'''<article class="card reveal"><div class="card-ico"><span class="doc-fmt">{fmt}</span></div><h3 class="card-title" data-i18n="{key}.title">{esc(title[0])}</h3><p data-i18n="{key}.body">{esc(body[0])}</p>
<a class="btn btn-primary" href="{href}" target="_blank" rel="noopener noreferrer"><span data-i18n="docs.open">{esc(cta[0])}</span></a></article>'''


def docs_section():
    cta = ('Abrir arquivo ↗', 'Open file ↗', '打开文件 ↗')
    cards = ''.join([
        doclink('docs.manual', 'PDF', 'assets/docs/manual-atendimento.pdf',
                ('Manual de processo e comandos de atendimento', 'Support process and commands manual', '客服流程与指令手册'),
                ('Guia de 11 páginas com o fluxo padrão de atendimento e as mensagens prontas para cada situação: identificação de conta, cadastro, login, depósito, saque via Pix, comprovantes e dados do cliente.',
                 '11-page guide with the standard support flow and ready-made messages for each situation: account identification, sign-up, login, deposits, Pix withdrawals, receipts and customer data.',
                 '共 11 页的指南，包含标准客服流程以及各种情况的现成话术：账户识别、注册、登录、充值、Pix 提现、凭证和客户资料。'), cta),
        doclink('docs.scripts', 'CSV', 'assets/docs/scripts-bonus.csv',
                ('Roteiro de mensagens de eventos e bônus', 'Event and bonus message scripts', '活动与奖金话术表'),
                ('Planilha com mensagens prontas para explicar promoções aos jogadores, como o evento de baú de convites, com as regras de depósito, aposta e saque do bônus.',
                 'Spreadsheet of ready-made messages for explaining promotions to players, such as the invitation treasure-chest event, including the deposit, betting and withdrawal rules for the bonus.',
                 '现成话术表，用于向玩家说明各类活动，例如邀请宝箱活动，包含奖金的充值、投注和提现规则。'), cta),
        doclink('docs.payroll', 'CSV', 'assets/docs/modelo-folha-mensal.csv',
                ('Modelo de folha de pagamento mensal', 'Monthly payroll template', '月度工资表模板'),
                ('Modelo em branco que usei para organizar a folha da equipe: data de admissão, salário-base, presença, bônus de desempenho, multas, adiantamentos e saldo a pagar.',
                 'Blank template I used to organise the team payroll: hire date, base salary, attendance, performance bonus, penalties, advances and remaining balance.',
                 '我用来整理团队工资的空白模板：入职日期、底薪、出勤、绩效奖金、罚款、预支和剩余工资。'), cta)])
    S('docs.note', 'Documentos de trabalho sem dados pessoais de funcionários ou clientes.', 'Work documents with no personal data of employees or customers.', '不含员工或客户个人信息的工作文档。')
    S('docs.sub', 'Materiais que criei e usei no Service Desk', 'Material I created and used at the Service Desk', '我在服务台工作中制作并使用的资料')
    return section('docs', 'docs.title', 'Documentos de trabalho', 'Materiais que criei e usei no Service Desk', 'docs.sub',
                   f'<div class="grid">{cards}</div>', h2vals=('Work documents', '工作文档'))


# fix: `explain` for Cambodia needs PT/EN/ZH title from PASS_H3; handled via the generic signature above.
def main():
    views = {'home': home, 'laos': laos, 'albania': albania, 'cambodia': cambodia, 'armenia': armenia, 'philippines': philippines}
    arts = ''
    for k in PAGES:
        S(f'meta.title.{k}', STR[f'country.{k}']['pt'], STR[f'country.{k}']['en'], STR[f'country.{k}']['zh'])
        arts += f'<article class="view" id="view-{k}" data-route="{k}" aria-labelledby="" hidden>\n{views[k]()}\n</article>\n'
    # aria-labelledby is set at runtime from the active h1; drop the empty attr
    arts = arts.replace(' aria-labelledby=""', '')
    tabs = ''.join(
        f'<li><a class="tab" href="#{k}" data-route-link="{k}">{flag(FLAG[k], 28) if k in FLAG else ""}{navimg(k)}</a></li>' for k in PAGES)
    langs = ''.join(f'<button type="button" data-lang="{c}" lang="{c}" aria-pressed="false">{n}</button>' for c, n in (('pt', 'PT'), ('en', 'EN'), ('zh', '中文')))
    person = {
        '@context': 'https://schema.org', '@type': 'Person', 'name': 'Vinícius Flórido Marques Costa',
        'jobTitle': 'Customer Service Analyst · Service Desk Coordinator',
        'nationality': {'@type': 'Country', 'name': 'Brazil'},
        'knowsLanguage': ['pt', 'en', 'es', 'zh'],
        'knowsAbout': ['Customer service', 'IT support', 'Service Desk management', 'Graphic design', 'SEO', 'Paid traffic'],
        'sameAs': ['https://github.com/boomrioseo-dev']}
    doc = f'''<!doctype html>
<html lang="pt-BR" data-lang="pt">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Início — {SITE_NAME}</title>
<meta name="description" content="{esc(STR["meta.description"]["pt"])}" data-i18n-content="meta.description">
<meta name="theme-color" content="#4a0508">
<meta name="color-scheme" content="dark">
<meta property="og:type" content="profile">
<meta property="og:title" content="Vinícius Flórido Marques Costa">
<meta property="og:description" content="{esc(STR["meta.description"]["pt"])}">
<meta property="og:image" content="assets/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap">
<link rel="stylesheet" href="css/tokens.css">
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/components.css">
<link rel="modulepreload" href="js/main.js">
<script type="application/ld+json">{json.dumps(person, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip-link" href="#main" data-i18n="ui.skip">{esc(STR["ui.skip"]["pt"])}</a>
<div class="vidbar" role="presentation"><video id="coin-strip" muted loop playsinline preload="metadata" poster="assets/video/coins-poster.webp" disablepictureinpicture aria-hidden="true" tabindex="-1" width="3840" height="320"><source src="assets/video/coins-4k.mp4" type="video/mp4"></video></div>
<header class="site-header">
<nav class="site-nav" aria-label="{esc(STR["ui.nav"]["pt"])}" data-i18n-aria="ui.nav">
<ul class="tabs" role="list">{tabs}</ul>
<div class="lang" role="group" aria-label="{esc(STR["ui.lang"]["pt"])}" data-i18n-aria="ui.lang">{langs}</div>
</nav>
</header>
<main id="main" tabindex="-1">
{arts}</main>
<div id="announcer" class="sr-only" role="status" aria-live="polite"></div>
<dialog id="lightbox" class="lightbox" aria-label="{esc(STR["ui.zoom"]["pt"])}" data-i18n-aria="ui.zoom">
<form method="dialog"><button class="lb-btn lb-close" data-i18n-aria="ui.close" aria-label="Fechar">×</button></form>
<button type="button" class="lb-btn lb-prev" data-i18n-aria="ui.prev" aria-label="Anterior">‹</button>
<img alt="" decoding="async">
<button type="button" class="lb-btn lb-next" data-i18n-aria="ui.next" aria-label="Próxima">›</button>
<p class="lb-cap"></p>
</dialog>
<noscript><style>.view[hidden]{{display:block}}.reveal{{opacity:1!important;transform:none!important}}</style></noscript>
<script type="module" src="js/main.js"></script>
</body>
</html>
'''
    open(f'{SITE}/index.html', 'w').write(doc)
    import os
    os.makedirs(f'{SITE}/i18n', exist_ok=True)
    for l in ('pt', 'en', 'zh'):
        d = {k: v[l] for k, v in sorted(STR.items())}
        json.dump(d, open(f'{SITE}/i18n/{l}.json', 'w'), ensure_ascii=False, indent=1)
    print('strings', len(STR), 'index.html', len(doc))


main()
