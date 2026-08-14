# Graph Report - .  (2026-08-10)

## Corpus Check
- 72 files · ~162,017 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 953 nodes · 1978 edges · 143 communities (132 shown, 11 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 131 edges (avg confidence: 0.66)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Analytics Cooking and Configurations
- Static Js
- Static Js
- Analytics Cooking and Configurations
- Analytics Tracking Core
- Static Js
- Analytics Event Enqueueing
- Analytics Event Enqueueing
- Analytics Third-party Integrations
- Analytics Third-party Integrations
- Model Unit Tests
- Static Js
- Default Navigation Controllers
- Analytics Third-party Integrations
- web2py Appadmin Database Interface
- Analytics Tracking Core
- Analytics Third-party Integrations
- Analytics Tracking Core
- Analytics Third-party Integrations
- Static Js Modernizr 2
- Analytics Third-party Integrations
- Analytics Third-party Integrations
- Analytics Cooking and Configurations
- Analytics Tracking Core
- Analytics Tracking Core
- Analytics Tracking Core
- Analytics Tracking Core
- Database Schema and PyDAL Tables
- Analytics Third-party Integrations
- Analytics Tracking Core
- Analytics Tracking Core
- Despachos Controller Endpoints
- Analytics Tracking Core
- Relatorios PDF Endpoints
- Analytics Tracking Core
- Analytics Third-party Integrations
- web2py Javascript Client Helpers
- web2py Javascript Client Helpers
- Database Schema and PyDAL Tables
- Analytics Tracking Core
- Analytics Cooking and Configurations
- Analytics Cooking and Configurations

## God Nodes (most connected - your core abstractions)
1. `call()` - 39 edges
2. `replace()` - 35 edges
3. `object()` - 24 edges
4. `Analytics()` - 23 edges
5. `TestTextosModelos` - 23 edges
6. `e()` - 22 edges
7. `parse()` - 17 edges
8. `f()` - 17 edges
9. `i()` - 17 edges
10. `clone()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `array()` --indirect_call--> `i()`  [INFERRED]
  static/js/analytics.min.js → static/js/bootstrap.bundle.min.js
- `invoke()` --indirect_call--> `e()`  [INFERRED]
  static/js/analytics.min.js → static/js/bootstrap.bundle.min.js
- `add()` --indirect_call--> `e()`  [INFERRED]
  static/js/analytics.min.js → static/js/bootstrap.bundle.min.js
- `attach()` --indirect_call--> `e()`  [INFERRED]
  static/js/analytics.min.js → static/js/bootstrap.bundle.min.js
- `ce()` --indirect_call--> `f()`  [INFERRED]
  static/js/jquery.3.5.1.js → static/js/analytics.min.js

## Import Cycles
- None detected.

## Communities (143 total, 11 thin omitted)

### Community 0 - "Analytics Cooking and Configurations"
Cohesion: 0.06
Nodes (15): check(), clear(), clone(), Cookie(), Entity(), Facade(), formatValue(), Group() (+7 more)

### Community 1 - "Static Js"
Cohesion: 0.06
Nodes (38): add(), attach(), f(), lowercase(), e(), ge(), $a(), B() (+30 more)

### Community 2 - "Static Js"
Cohesion: 0.07
Nodes (35): z(), P(), A(), b(), be(), Bt(), ce(), ct() (+27 more)

### Community 3 - "Analytics Cooking and Configurations"
Cohesion: 0.07
Nodes (10): Analytics(), canonicalPath(), canonicalUrl(), defaults(), Emitter(), mixin(), normalize(), object() (+2 more)

### Community 4 - "Analytics Tracking Core"
Cohesion: 0.09
Nodes (5): handler(), prefix(), props(), Screen(), _wrapTrack()

### Community 5 - "Static Js"
Cohesion: 0.13
Nodes (28): at(), B(), bt(), ct(), dt(), F(), ft(), G() (+20 more)

### Community 6 - "Analytics Event Enqueueing"
Cohesion: 0.07
Nodes (12): enqueue(), experiments(), find(), isAbsolute(), isFunction(), isRelative(), multiple(), objectify() (+4 more)

### Community 7 - "Analytics Event Enqueueing"
Cohesion: 0.12
Nodes (3): currency(), ecommerce(), track()

### Community 8 - "Analytics Third-party Integrations"
Cohesion: 0.07
Nodes (4): global(), onError(), push(), unique()

### Community 10 - "Model Unit Tests"
Cohesion: 0.13
Nodes (7): Despachar(), determinar_despacho(), dict_condicoes_de_templates(), patch, # TODO: Add tests for Despachar function, This method is called before each test. We reset mocks here to ensure test…, TestTextosModelos

### Community 11 - "Static Js"
Cohesion: 0.09
Nodes (4): H(), J(), S(), N()

### Community 13 - "Default Navigation Controllers"
Cohesion: 0.13
Nodes (20): action, api_get_user_email(), Bairros(), Despachar_Processos(), download(), editar_laudo(), Especies(), fotos() (+12 more)

### Community 14 - "Analytics Third-party Integrations"
Cohesion: 0.12
Nodes (4): api(), del(), formatDate(), omit()

### Community 15 - "web2py Appadmin Database Interface"
Cohesion: 0.18
Nodes (15): ccache(), csv(), d3_graph_model(), download(), eval_in_global_env(), get_database(), get_query(), get_table() (+7 more)

### Community 16 - "Analytics Tracking Core"
Cohesion: 0.12
Nodes (20): clean(), defaultNormalize(), flatten(), ieKeyFix(), left(), map(), replace(), right() (+12 more)

### Community 17 - "Analytics Third-party Integrations"
Cohesion: 0.14
Nodes (4): bind(), bindMethods(), throttle(), when()

### Community 19 - "Analytics Third-party Integrations"
Cohesion: 0.14
Nodes (9): ads(), all(), array(), domain(), is(), isCrossDomain(), parse(), port() (+1 more)

### Community 20 - "Static Js Modernizr 2"
Cohesion: 0.28
Nodes (15): b(), D(), E(), F(), G(), H(), I(), J() (+7 more)

### Community 22 - "Analytics Third-party Integrations"
Cohesion: 0.14
Nodes (11): call(), callback(), generate(), https(), invoke(), merge(), pick(), queue() (+3 more)

### Community 23 - "Analytics Cooking and Configurations"
Cohesion: 0.29
Nodes (3): enhancedEcommerceProductAction(), enhancedEcommerceTrackProduct(), extractCheckoutOptions()

### Community 26 - "Analytics Tracking Core"
Cohesion: 0.20
Nodes (8): Alias(), aliasByDictionary(), aliasByFunction(), convert(), determineCase(), isFloat(), isInt(), string()

### Community 27 - "Analytics Tracking Core"
Cohesion: 0.20
Nodes (10): coerce(), color(), debug(), error(), fmt(), humanize(), load(), loadImage() (+2 more)

### Community 28 - "Database Schema and PyDAL Tables"
Cohesion: 0.28
Nodes (5): buscador(), Modal(), padronizaprotoc(), ProtocPattern, Cria um elemento modal html com titulo e informações a receber

### Community 31 - "Analytics Tracking Core"
Cohesion: 0.29
Nodes (6): get(), mapping(), option(), quote(), str(), stripNested()

### Community 32 - "Despachos Controller Endpoints"
Cohesion: 0.33
Nodes (3): Gerenciar_Modelos(), requires_login, Controller para gerenciar templates de despacho

### Community 33 - "Analytics Tracking Core"
Cohesion: 0.33
Nodes (5): base64(), encode(), jsonp(), set(), stringify()

### Community 34 - "Relatorios PDF Endpoints"
Cohesion: 0.60
Nodes (4): Podas_por_periodo(), relat_podas_periodo(), relat_supress_periodo(), Supressões_por_periodo()

### Community 35 - "Analytics Tracking Core"
Cohesion: 0.50
Nodes (5): defaultToFunction(), objectToFunction(), regexpToFunction(), stringToFunction(), toFunction()

### Community 36 - "Analytics Third-party Integrations"
Cohesion: 0.50
Nodes (3): isEmpty(), length(), metrics()

### Community 37 - "web2py Javascript Client Helpers"
Cohesion: 0.60
Nodes (3): ml(), pe(), rel()

### Community 38 - "web2py Javascript Client Helpers"
Cohesion: 0.60
Nodes (3): ml(), pe(), rel()

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `f()` connect `Static Js` to `Static Js`, `Analytics Event Enqueueing`, `Analytics Tracking Core`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `e()` connect `Static Js` to `Analytics Tracking Core`, `Static Js`, `Analytics Cooking and Configurations`, `Static Js`, `Static Js Modernizr 2`, `Analytics Third-party Integrations`, `Analytics Third-party Integrations`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `g()` connect `Static Js` to `Static Js`, `Static Js`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `Analytics Cooking and Configurations` be split into smaller, more focused modules?**
  _Cohesion score 0.056051587301587304 - nodes in this community are weakly interconnected._
- **Should `Static Js` be split into smaller, more focused modules?**
  _Cohesion score 0.05764145954521417 - nodes in this community are weakly interconnected._
- **Should `Static Js` be split into smaller, more focused modules?**
  _Cohesion score 0.07111756168359942 - nodes in this community are weakly interconnected._
- **Should `Analytics Cooking and Configurations` be split into smaller, more focused modules?**
  _Cohesion score 0.06648936170212766 - nodes in this community are weakly interconnected._