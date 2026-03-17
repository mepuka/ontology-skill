"""Generate a static HTML ontology viewer from the Energy News Ontology.

Pre-processes all RDF data into JSON and embeds it in a self-contained HTML
file with zero external dependencies. Opens instantly in any browser.
"""

import json
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS

ENEWS = Namespace("http://example.org/ontology/energy-news#")
SH = Namespace("http://www.w3.org/ns/shacl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
BFO = Namespace("http://purl.obolibrary.org/obo/")
SCHEMA = Namespace("https://schema.org/")

BASE_DIR = Path(__file__).parent.parent
TBOX_PATH = BASE_DIR / "energy-news.ttl"
REF_PATH = BASE_DIR / "energy-news-reference-individuals.ttl"
SHAPES_PATH = BASE_DIR / "shapes" / "energy-news-shapes.ttl"
BFO_PATH = BASE_DIR / "imports" / "bfo-declarations.ttl"
SCHEMA_PATH = BASE_DIR / "imports" / "schema-declarations.ttl"
OUTPUT_PATH = BASE_DIR / "docs" / "ontology-viewer.html"

BFO_LABELS = {
    "BFO_0000015": "Process",
    "BFO_0000029": "Site",
    "BFO_0000030": "Object",
    "BFO_0000031": "GDC",
}


def short(uri: URIRef | str) -> str:
    """Get a short display name from a URI."""
    s = str(uri)
    if "#" in s:
        return s.split("#")[-1]
    return s.rsplit("/", 1)[-1]


def extract_classes(g: Graph) -> list[dict]:
    """Extract all OWL classes with metadata."""
    classes = []
    for cls in g.subjects(RDF.type, OWL.Class):
        if not isinstance(cls, URIRef) or not str(cls).startswith(str(ENEWS)):
            continue
        name = short(cls)
        label = str(g.value(cls, RDFS.label, default=name))
        definition = str(g.value(cls, SKOS.definition, default=""))

        # Find BFO parent
        bfo_parent = ""
        parents = []
        for parent in g.objects(cls, RDFS.subClassOf):
            if isinstance(parent, URIRef):
                pname = short(parent)
                if pname.startswith("BFO_"):
                    bfo_parent = BFO_LABELS.get(pname, pname)
                elif str(parent).startswith(str(ENEWS)):
                    parents.append(short(parent))
                elif str(parent).startswith(str(SCHEMA)):
                    parents.append(f"schema:{short(parent)}")

        classes.append(
            {
                "uri": name,
                "label": label,
                "definition": definition,
                "bfo_parent": bfo_parent,
                "parents": parents,
            }
        )

    return sorted(classes, key=lambda c: c["label"])


def extract_properties(g: Graph) -> list[dict]:
    """Extract all properties with metadata."""
    props = []
    for prop_type, type_label in [
        (OWL.ObjectProperty, "Object"),
        (OWL.DatatypeProperty, "Data"),
    ]:
        for prop in g.subjects(RDF.type, prop_type):
            if not isinstance(prop, URIRef) or not str(prop).startswith(str(ENEWS)):
                continue
            name = short(prop)
            label = str(g.value(prop, RDFS.label, default=name))
            domain = short(g.value(prop, RDFS.domain, default=URIRef("")))
            rng = short(g.value(prop, RDFS.range, default=URIRef("")))
            functional = (prop, RDF.type, OWL.FunctionalProperty) in g
            definition = str(g.value(prop, SKOS.definition, default=""))

            props.append(
                {
                    "uri": name,
                    "label": label,
                    "type": type_label,
                    "domain": domain,
                    "range": rng,
                    "functional": functional,
                    "definition": definition,
                }
            )

    return sorted(props, key=lambda p: (p["type"], p["label"]))


def extract_shapes(g: Graph) -> list[dict]:
    """Extract SHACL shapes with their constraints."""
    shapes = []
    for shape in g.subjects(RDF.type, SH.NodeShape):
        name = short(shape)
        target = short(g.value(shape, SH.targetClass, default=URIRef("")))

        constraints = []
        for prop_node in g.objects(shape, SH.property):
            path = short(g.value(prop_node, SH.path, default=URIRef("")))
            min_c = g.value(prop_node, SH.minCount)
            max_c = g.value(prop_node, SH.maxCount)
            dt = g.value(prop_node, SH.datatype)
            cls = g.value(prop_node, SH["class"])

            constraint = {"path": path}
            if min_c is not None:
                constraint["minCount"] = int(min_c)
            if max_c is not None:
                constraint["maxCount"] = int(max_c)
            if dt is not None:
                constraint["datatype"] = short(dt)
            if cls is not None:
                constraint["class"] = short(cls)
            constraints.append(constraint)

        # Check for SPARQL constraints
        has_sparql = any(True for _ in g.objects(shape, SH.sparql))

        shapes.append(
            {
                "name": name,
                "targetClass": target,
                "constraints": sorted(constraints, key=lambda c: c["path"]),
                "hasSparql": has_sparql,
            }
        )

    return sorted(shapes, key=lambda s: s["name"])


def extract_topics(g: Graph) -> list[dict]:
    """Extract SKOS topic hierarchy."""
    topics = []
    for concept in g.subjects(RDF.type, ENEWS.EnergyTopic):
        if not isinstance(concept, URIRef):
            continue
        name = short(concept)
        label = str(g.value(concept, RDFS.label, default=name))
        definition = str(g.value(concept, SKOS.definition, default=""))
        broader = [short(b) for b in g.objects(concept, SKOS.broader) if isinstance(b, URIRef)]
        is_top = (concept, SKOS.topConceptOf, None) in g

        alt_labels = [str(al) for al in g.objects(concept, SKOS.altLabel)]

        topics.append(
            {
                "uri": name,
                "label": label,
                "definition": definition,
                "broader": broader,
                "isTop": is_top,
                "altLabels": alt_labels,
            }
        )

    return sorted(topics, key=lambda t: t["label"])


def extract_individuals(g: Graph) -> dict[str, list[dict]]:
    """Extract reference individuals grouped by type."""
    groups: dict[str, list[dict]] = {
        "Organization": [],
        "RegulatoryBody": [],
        "GeographicEntity": [],
        "Publication": [],
        "SocialMediaPlatform": [],
        "Feed": [],
        "ProjectStatus": [],
    }

    type_map = {
        ENEWS.Organization: "Organization",
        ENEWS.RegulatoryBody: "RegulatoryBody",
        ENEWS.GeographicEntity: "GeographicEntity",
        ENEWS.Publication: "Publication",
        ENEWS.SocialMediaPlatform: "SocialMediaPlatform",
        ENEWS.Feed: "Feed",
        ENEWS.ProjectStatus: "ProjectStatus",
    }

    for type_uri, group_name in type_map.items():
        for ind in g.subjects(RDF.type, type_uri):
            if not isinstance(ind, URIRef):
                continue
            name = short(ind)
            label = str(g.value(ind, RDFS.label, default=name))
            definition = str(g.value(ind, SKOS.definition, default=""))

            entry = {"uri": name, "label": label, "definition": definition}

            # Extra fields per type
            if group_name == "Publication":
                sd = g.value(ind, ENEWS.siteDomain)
                if sd:
                    entry["siteDomain"] = str(sd)
            elif group_name in ("Organization", "RegulatoryBody"):
                sectors = [
                    str(g.value(s, RDFS.label, default=short(s)))
                    for s in g.objects(ind, ENEWS.hasSector)
                ]
                if sectors:
                    entry["sectors"] = sectors

            # Don't double-count RegulatoryBody as Organization
            if group_name == "Organization" and (ind, RDF.type, ENEWS.RegulatoryBody) in g:
                continue

            groups[group_name].append(entry)

    for group in groups.values():
        group.sort(key=lambda x: x["label"])

    return groups


def generate_html(data: dict) -> str:
    """Generate the full HTML page from extracted data."""
    data_json = json.dumps(data, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Energy News Ontology Viewer</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: #f5f6fa; color: #2d3436; line-height: 1.6; }}
header {{ background: #1e272e; color: white; padding: 1.5rem 2rem; }}
header h1 {{ font-size: 1.8rem; font-weight: 700; }}
header p {{ opacity: 0.8; margin-top: 0.3rem; font-size: 0.95rem; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 1.5rem; }}

/* Stats cards */
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem; margin-bottom: 1.5rem; }}
.stat-card {{ background: white; border-radius: 10px; padding: 1.2rem;
  text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.stat-card .num {{ font-size: 2rem; font-weight: 800; color: #0984e3; }}
.stat-card .lbl {{ font-size: 0.85rem; color: #636e72; text-transform: uppercase;
  letter-spacing: 0.5px; }}

/* Panels */
.panel {{ background: white; border-radius: 10px; margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); overflow: hidden; }}
.panel-header {{ padding: 1rem 1.5rem; cursor: pointer; display: flex;
  align-items: center; justify-content: space-between; border-bottom: 1px solid #eee;
  user-select: none; }}
.panel-header:hover {{ background: #f8f9fa; }}
.panel-header h2 {{ font-size: 1.15rem; font-weight: 600; }}
.panel-header .chevron {{ transition: transform 0.2s; font-size: 1.2rem; color: #636e72; }}
.panel-header.collapsed .chevron {{ transform: rotate(-90deg); }}
.panel-body {{ padding: 1.5rem; }}
.panel-body.hidden {{ display: none; }}

/* Badges */
.badge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px;
  font-size: 0.75rem; font-weight: 600; margin-left: 0.3rem; }}
.badge-green {{ background: #00b894; color: white; }}
.badge-amber {{ background: #fdcb6e; color: #2d3436; }}
.badge-blue {{ background: #0984e3; color: white; }}
.badge-purple {{ background: #6c5ce7; color: white; }}
.badge-red {{ background: #d63031; color: white; }}
.badge-gray {{ background: #b2bec3; color: white; }}

/* Class tree */
.tree {{ padding-left: 0; }}
.tree ul {{ padding-left: 1.5rem; }}
.tree li {{ list-style: none; padding: 0.3rem 0; }}
.class-node {{ display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.3rem 0.7rem; border-radius: 6px; font-size: 0.9rem; }}
.class-node.shaped {{ background: #d4edda; }}
.class-node.unshaped {{ background: #fff3cd; }}
.class-node .cls-name {{ font-weight: 600; }}
.tree details > summary {{ cursor: pointer; list-style: none; }}
.tree details > summary::-webkit-details-marker {{ display: none; }}
.tree details > summary::before {{ content: '\\25B6'; display: inline-block;
  margin-right: 0.4rem; font-size: 0.7rem; transition: transform 0.15s; color: #636e72; }}
.tree details[open] > summary::before {{ transform: rotate(90deg); }}
.def-tooltip {{ display: none; position: absolute; background: #2d3436; color: white;
  padding: 0.5rem 0.8rem; border-radius: 6px; font-size: 0.8rem; max-width: 400px;
  z-index: 100; line-height: 1.4; }}
.class-node:hover .def-tooltip {{ display: block; }}
.class-node {{ position: relative; }}

/* Property table */
table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
th {{ text-align: left; padding: 0.6rem 0.8rem; background: #f8f9fa;
  border-bottom: 2px solid #dfe6e9; font-weight: 600; font-size: 0.8rem;
  text-transform: uppercase; letter-spacing: 0.3px; color: #636e72; }}
td {{ padding: 0.6rem 0.8rem; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #f8f9fa; }}

/* Shape cards */
.shape-card {{ border: 1px solid #dfe6e9; border-radius: 8px; padding: 1rem;
  margin-bottom: 0.8rem; }}
.shape-card h3 {{ font-size: 1rem; margin-bottom: 0.5rem; }}
.shape-card .constraint {{ font-size: 0.85rem; padding: 0.2rem 0;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; }}

/* Topic tree */
.topic-tree {{ column-count: 2; column-gap: 2rem; }}
@media (max-width: 768px) {{ .topic-tree {{ column-count: 1; }} }}
.topic-group {{ break-inside: avoid; margin-bottom: 1rem; }}
.topic-group h3 {{ font-size: 0.95rem; color: #0984e3; margin-bottom: 0.3rem;
  padding: 0.3rem 0.6rem; background: #e3f2fd; border-radius: 4px;
  display: inline-block; }}
.topic-leaf {{ font-size: 0.85rem; padding: 0.15rem 0 0.15rem 1.2rem; color: #555; }}
.topic-leaf .alt {{ color: #999; font-style: italic; }}

/* Individual chips */
.ind-group {{ margin-bottom: 1rem; }}
.ind-group h3 {{ font-size: 0.95rem; margin-bottom: 0.5rem; color: #636e72; }}
.chip-list {{ display: flex; flex-wrap: wrap; gap: 0.4rem; }}
.chip {{ padding: 0.3rem 0.7rem; background: #eee; border-radius: 20px;
  font-size: 0.85rem; cursor: default; position: relative; }}
.chip:hover {{ background: #d5d8dc; }}
.chip .chip-tip {{ display: none; position: absolute; bottom: 100%; left: 0;
  background: #2d3436; color: white; padding: 0.4rem 0.6rem; border-radius: 6px;
  font-size: 0.78rem; max-width: 300px; white-space: normal; z-index: 50;
  margin-bottom: 0.3rem; }}
.chip:hover .chip-tip {{ display: block; }}
</style>
</head>
<body>
<header>
  <h1>Energy News Ontology Viewer</h1>
  <p>v0.3.0 &mdash; Phase 1 Pre-ABox Readiness &mdash; {data["stats"]["triple_count"]} triples</p>
</header>
<div class="container" id="app"></div>

<script>
const DATA = {data_json};

function togglePanel(el) {{
  const body = el.nextElementSibling;
  body.classList.toggle('hidden');
  el.classList.toggle('collapsed');
}}

function renderStats(stats) {{
  const items = [
    ['Classes', stats.class_count, '#0984e3'],
    ['Properties', stats.property_count, '#00b894'],
    ['SHACL Shapes', stats.shape_count, '#6c5ce7'],
    ['Energy Topics', stats.topic_count, '#e17055'],
    ['Ref. Individuals', stats.individual_count, '#fdcb6e'],
    ['Triples', stats.triple_count, '#636e72'],
  ];
  return '<div class="stats">' + items.map(([lbl, num, color]) =>
    `<div class="stat-card"><div class="num" style="color:${{color}}">${{num}}</div>` +
    `<div class="lbl">${{lbl}}</div></div>`
  ).join('') + '</div>';
}}

function renderClassTree(classes, shapedClasses) {{
  // Build hierarchy: group by BFO parent, then show subclasses
  const bfoGroups = {{}};
  const childMap = {{}};

  classes.forEach(c => {{
    if (c.bfo_parent) bfoGroups[c.bfo_parent] = bfoGroups[c.bfo_parent] || [];
    if (c.bfo_parent && c.parents.length === 0) {{
      bfoGroups[c.bfo_parent].push(c);
    }}
    c.parents.forEach(p => {{
      childMap[p] = childMap[p] || [];
      childMap[p].push(c);
    }});
  }});

  // Also add classes with enews parents to their BFO group via parent
  classes.forEach(c => {{
    if (c.parents.length > 0 && !c.bfo_parent) {{
      // Find parent's BFO group
      const parent = classes.find(p => p.uri === c.parents[0]);
      if (parent && parent.bfo_parent) {{
        // Already handled as child
      }}
    }}
  }});

  function renderNode(c) {{
    const shaped = shapedClasses.has(c.uri);
    const cls = shaped ? 'shaped' : 'unshaped';
    const badge = shaped
      ? '<span class="badge badge-green">SHACL</span>'
      : '<span class="badge badge-amber">no shape</span>';
    const children = childMap[c.uri] || [];
    const defText = c.definition ? `<span class="def-tooltip">${{c.definition}}</span>` : '';

    let html = `<span class="class-node ${{cls}}">` +
      `<span class="cls-name">${{c.label}}</span>${{badge}}${{defText}}</span>`;

    if (children.length > 0) {{
      html = `<details open><summary>${{html}}</summary><ul>` +
        children.map(ch => `<li>${{renderNode(ch)}}</li>`).join('') +
        `</ul></details>`;
    }}
    return html;
  }}

  let html = '<div class="tree"><ul>';
  const bfoOrder = ['Process', 'Site', 'Object', 'GDC'];
  bfoOrder.forEach(bfo => {{
    const group = bfoGroups[bfo] || [];
    if (group.length === 0) return;
    html += `<li><details open><summary>` +
      `<span class="badge badge-purple">${{bfo}}</span></summary><ul>`;
    group.forEach(c => {{
      html += `<li>${{renderNode(c)}}</li>`;
    }});
    html += '</ul></details></li>';
  }});
  html += '</ul></div>';
  return html;
}}

function renderProperties(props) {{
  let html = '<table><thead><tr><th>Name</th><th>Type</th>' +
    '<th>Domain</th><th>Range</th><th>Traits</th></tr></thead><tbody>';
  props.forEach(p => {{
    const typeBadge = p.type === 'Object'
      ? '<span class="badge badge-blue">OBJ</span>'
      : '<span class="badge badge-green">DATA</span>';
    const traits = p.functional ? '<span class="badge badge-gray">functional</span>' : '';
    html += `<tr><td title="${{p.definition}}"><strong>${{p.label}}</strong></td>` +
      `<td>${{typeBadge}}</td><td>${{p.domain || '&mdash;'}}</td>` +
      `<td>${{p.range || '&mdash;'}}</td><td>${{traits}}</td></tr>`;
  }});
  html += '</tbody></table>';
  return html;
}}

function renderShapes(shapes) {{
  return shapes.map(s => {{
    const sparqlNote = s.hasSparql ? ' <span class="badge badge-purple">+ SPARQL</span>' : '';
    const rows = s.constraints.map(c => {{
      const parts = [`<strong>${{c.path}}</strong>`];
      if (c.minCount !== undefined) parts.push(`min: ${{c.minCount}}`);
      if (c.maxCount !== undefined) parts.push(`max: ${{c.maxCount}}`);
      if (c.datatype) parts.push(`type: ${{c.datatype}}`);
      if (c['class']) parts.push(`class: ${{c['class']}}`);
      return `<div class="constraint">${{parts.join(' &nbsp;|&nbsp; ')}}</div>`;
    }}).join('');
    return `<div class="shape-card"><h3>${{s.name}} &rarr; ` +
      `<span class="badge badge-blue">${{s.targetClass}}</span>` +
      `${{sparqlNote}}</h3>${{rows}}</div>`;
  }}).join('');
}}

function renderTopics(topics) {{
  const topTopics = topics.filter(t => t.isTop);
  const childMap = {{}};
  topics.forEach(t => {{
    t.broader.forEach(b => {{
      childMap[b] = childMap[b] || [];
      childMap[b].push(t);
    }});
  }});

  return '<div class="topic-tree">' + topTopics.map(top => {{
    const children = childMap[top.uri] || [];
    const childHtml = children.map(c => {{
      const alts = c.altLabels.length > 0
        ? ` <span class="alt">(${{c.altLabels.join(', ')}})</span>`
        : '';
      return `<div class="topic-leaf" title="${{c.definition}}">${{c.label}}${{alts}}</div>`;
    }}).join('');
    return `<div class="topic-group"><h3>${{top.label}}</h3>${{childHtml}}</div>`;
  }}).join('') + '</div>';
}}

function renderIndividuals(groups) {{
  const labels = {{
    'Organization': 'Organizations',
    'RegulatoryBody': 'Regulatory Bodies',
    'GeographicEntity': 'Geographic Entities',
    'Publication': 'Publications',
    'SocialMediaPlatform': 'Social Media Platforms',
    'Feed': 'Feeds',
    'ProjectStatus': 'Project Statuses',
  }};
  return Object.entries(groups).map(([key, items]) => {{
    if (items.length === 0) return '';
    const chips = items.map(i => {{
      let extra = '';
      if (i.siteDomain) extra = ` (${{i.siteDomain}})`;
      if (i.sectors) extra = ` [${{i.sectors.join(', ')}}]`;
      const tip = i.definition ? `<span class="chip-tip">${{i.definition}}</span>` : '';
      return `<span class="chip">${{i.label}}${{extra}}${{tip}}</span>`;
    }}).join('');
    return `<div class="ind-group">` +
      `<h3>${{labels[key] || key}} (${{items.length}})</h3>` +
      `<div class="chip-list">${{chips}}</div></div>`;
  }}).join('');
}}

function render() {{
  const shapedClasses = new Set(DATA.shapes.map(s => s.targetClass));
  const app = document.getElementById('app');

  let html = renderStats(DATA.stats);

  const panels = [
    ['Class Hierarchy', renderClassTree(DATA.classes, shapedClasses)],
    ['Properties (' + DATA.properties.length + ')', renderProperties(DATA.properties)],
    ['SHACL Shapes (' + DATA.shapes.length + ')', renderShapes(DATA.shapes)],
    ['Energy Topics (' + DATA.topics.length + ')', renderTopics(DATA.topics)],
    ['Reference Individuals', renderIndividuals(DATA.individuals)],
  ];

  panels.forEach(([title, content]) => {{
    html += `<div class="panel">` +
      `<div class="panel-header" onclick="togglePanel(this)">` +
      `<h2>${{title}}</h2><span class="chevron">&#9660;</span></div>` +
      `<div class="panel-body">${{content}}</div></div>`;
  }});

  app.innerHTML = html;
}}

render();
</script>
</body>
</html>"""


def main() -> None:
    """Generate the ontology viewer HTML."""
    print("Loading ontology files...")
    g = Graph()
    g.parse(TBOX_PATH, format="turtle")
    g.parse(REF_PATH, format="turtle")
    g.parse(BFO_PATH, format="turtle")
    g.parse(SCHEMA_PATH, format="turtle")

    shapes_g = Graph()
    shapes_g.parse(SHAPES_PATH, format="turtle")

    print(f"  Loaded {len(g)} triples (ontology) + {len(shapes_g)} triples (shapes)")

    print("Extracting data...")
    classes = extract_classes(g)
    properties = extract_properties(g)
    shapes = extract_shapes(shapes_g)
    topics = extract_topics(g)
    individuals = extract_individuals(g)

    shaped_classes = {s["targetClass"] for s in shapes}
    ind_count = sum(len(v) for v in individuals.values())

    data = {
        "stats": {
            "class_count": len(classes),
            "property_count": len(properties),
            "shape_count": len(shapes),
            "topic_count": len(topics),
            "individual_count": ind_count,
            "triple_count": len(g) + len(shapes_g),
        },
        "classes": classes,
        "properties": properties,
        "shapes": shapes,
        "topics": topics,
        "individuals": individuals,
    }

    print(f"  {len(classes)} classes ({len(shaped_classes)} with shapes)")
    print(f"  {len(properties)} properties")
    print(f"  {len(shapes)} SHACL shapes")
    print(f"  {len(topics)} energy topics")
    print(f"  {ind_count} reference individuals")

    html = generate_html(data)
    OUTPUT_PATH.write_text(html)
    print(f"\nViewer written to {OUTPUT_PATH} ({len(html) // 1024}KB)")


if __name__ == "__main__":
    main()
