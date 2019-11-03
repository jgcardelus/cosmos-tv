//DEFINING PAGE
let scanTabs = new Tabs(0, "scan");
scanTabs.create();
tabs.push(scanTabs);

//PAGE ACTIVATION AND DEACTIVATION
let scanPopup = new Popup("scan", scanTabs, appTabs);

// PAGE BEHAVIOUR
let jsonExample = `
    {"scan-result": [{
            "name": "Big Mouth",
            "url": "some url",
            "id": "1",
            "seasons":[{
                "name": "Season 1",
                "id": "1-s1",
                "episodes": [{
                    "name": "Episode 1",
                    "id": "1-s1-ep1",
                    "url": "some url"
                },
                {
                    "name": "Episode 2",
                    "id": "1-s1-ep2",
                    "url": "some url"
                }]
            }, {
                "name": "Season 2",
                "id": "1-s2",
                "episodes": [{
                    "name": "Episode 1",
                    "id": "1-s2-ep1",
                    "url": "some url"
                },
                {
                    "name": "Episode 2",
                    "id": "1-s2-ep2",
                    "url": "some url"
                }]
            }]
        },{
            "name": "Family Guy",
            "url": "some url",
            "id": "2",
            "seasons":[{
                "name": "Season 1",
                "id": "2-s1",
                "episodes": [{
                    "name": "Episode 1",
                    "id": "2-s1-ep1",
                    "url": "some url"
                },
                {
                    "name": "Episode 2",
                    "id": "2-s1-ep2",
                    "url": "some url"
                }]
            }]
        },{
            "name": "Pulp Fiction",
            "id": "3",
            "url": "some url",
            "seasons":[]
        }]
    }
`;

class ExpandableElement {
	constructor(id, children) {
		this.id = id;
		this.children = children;
		this.expanded = true;

		this.expandIcon = "expand_more";
		this.contractIcon = "expand_less";

		this.animationTime = 300;
	}

	create() {
		this.events();
		this.contractFast();
	}

	events() {
		let selector = "#" + this.id + " #exp-" + this.id;
		$(selector).on("click", e => {
			this.expanderHandler();
		});
	}

	expanderHandler() {
		if (this.expanded) {
			this.contract();
		} else {
			this.expand();
		}
	}

	contractFast() {
		$("#" + this.id + " ." + this.children).slideUp(0, e => {
			this.expanded = false;
		});
	}

	contract() {
		$("#" + this.id + " ." + this.children).slideUp(
			this.animationTime,
			e => {
				this.expanded = false;
			}
		);

		let spanSelector = "#exp-" + this.id + " span";
		$(spanSelector).slideUp(this.animationTime / 2, e => {
			$(spanSelector).html(this.expandIcon);
			$(spanSelector).slideDown(this.animationTime / 2);
		});
	}

	expand() {
		$("#" + this.id + " ." + this.children).slideDown(
			this.animationTime,
			e => {
				this.expanded = true;
			}
		);

		let spanSelector = "#exp-" + this.id + " span";
		$(spanSelector).slideUp(this.animationTime / 2, e => {
			$(spanSelector).html(this.contractIcon);
			$(spanSelector).slideDown(this.animationTime / 2);
		});
	}
}

class URLElement {
	constructor(id, url) {
		this.id = id;
		this.url = url;
	}

	create() {
		this.events();
	}

	events() {
		$("#" + this.id).on("click", e => {
			this.handleURL();
		});
	}

	handleURL() {
		console.log(this.url);
	}
}

class Expandable {
	constructor(id) {
		this.id = id;
		this.selector = ".card-container#" + id;
		this.dataset = null;
		this.parsedHTML = "";

		this.expandableElements = [];
		this.urlELements = [];
	}

	create(raw_dataset) {
		let dataset = JSON.parse(raw_dataset);
		this.dataset = dataset;
		this.parsedHTML = "";

		//Unbind events
		$(this.selector).unbind();
		//Clear html
		$(this.selector).html("");
		for (let show of dataset[this.id]) {
			if (show["seasons"].length == 0) {
				this.injectShow(show);
			} else {
				this.injectExpandableShow(show);
			}
		}

		this.createUrls();
		this.createExpandables();
		this.addMDC();
	}

	createUrls() {
		for (let element of this.urlELements) {
			element.create();
		}
	}

	createExpandables() {
		for (let element of this.expandableElements) {
			element.create();
		}
	}

	addMDC() {
		let selectorPrefix = "#" + this.id;
		$(selectorPrefix + " .button").addClass("mdc-ripple-surface");
		$(selectorPrefix + " .button").attr("data-mdc-auto-init", "MDCRipple");

		$(selectorPrefix + " .round-button").addClass("mdc-ripple-surface");
		$(selectorPrefix + " .round-button").attr(
			"data-mdc-auto-init",
			"MDCRipple"
		);

		$(selectorPrefix + " .fab").addClass("mdc-ripple-surface");
		$(selectorPrefix + " .fab").attr("data-mdc-auto-init", "MDCRipple");

		$(selectorPrefix + " .card").addClass("mdc-elevation--z4");

		$(selectorPrefix + " .mdc-icon-button").attr(
			"data-mdc-auto-init",
			"MDCRipple"
		);
		$(selectorPrefix + " .mdc-fab").attr("data-mdc-auto-init", "MDCRipple");

		mdc.autoInit();
	}

	injectShow(dataset) {
		let name = dataset["name"];
		let id = dataset["id"];

		//URL Element
		let urlElement = new URLElement("url-" + id, dataset["url"]);
		this.urlELements.push(urlElement);

		let component = this.createShow(name, id);
		$(this.selector).append(component);
	}

	injectExpandableShow(dataset) {
		let name = dataset["name"];
		let id = dataset["id"];

		//URL Element
		let urlElement = new URLElement("url-" + id, dataset["url"]);
		this.urlELements.push(urlElement);

		let component = this.createExpandableShow(name, id);
		$(this.selector).append(component);

		this.injectSeason(dataset["seasons"], id);
	}

	injectSeason(dataset, containerId) {
		for (let i = 0; i < dataset.length; i++) {
			let season = dataset[i];

			let name = season["name"];
			let id = season["id"];
			let component = this.createSeason(name, id);
			$("#" + containerId).append(component);

			if (i + 1 == dataset.length) {
				$("#" + id).css("margin-bottom", "var(--border-size)");
			}

			this.injectEpisode(season["episodes"], id);
		}
	}

	injectEpisode(dataset, containerId) {
		for (let episode of dataset) {
			let name = episode["name"];
			let id = episode["id"];

			//URL Element
			let urlElement = new URLElement("url-" + id, episode["url"]);
			this.urlELements.push(urlElement);

			let component = this.createEpisode(name, id);
			$("#" + containerId + " .expandee").append(component);
		}
	}

	createShow(name, id) {
		let component =
			`
        <div class="card card-action round"  id="` +
			id +
			`">
            <button class="button primary round-left" id="url-` +
			id +
			`">
                <h2>` +
			name +
			`</h2>
            </button>
        </div>`;
		return component;
	}

	createExpandableShow(name, id) {
		let component =
			`
        <div class="expandable-card" id="` +
			id +
			`">
            <div class="card card-action side-button round">
                <button class="button primary round-left" id="url-` +
			id +
			`">
                    <h2>` +
			name +
			`</h2>
                </button>
                <button class="button secondary round-right" id="exp-` +
			id +
			`">
                    <span class="icons">expand_more</span>
                </button>
            </div>
        </div>`;

		let expandableElement = new ExpandableElement(id, "expandable");
		this.expandableElements.push(expandableElement);
		return component;
	}

	createSeason(name, id) {
		let component =
			`
        <div class="expandable section-card" id="` +
			id +
			`">
            <div class="section-header side-button">
                <button class="button transparent expander" id="exp-` +
			id +
			`">
                    <h2>` +
			name +
			`</h2>
                    <span class="icons">expand_more</span>
                </button>
            </div>
            <div class="expandee"></div>
        </div>`;
		let expandableElement = new ExpandableElement(id, "expandee");
		this.expandableElements.push(expandableElement);
		return component;
	}

	createEpisode(name, id) {
		let component =
			`
        <div class="section-action" id="` +
			id +
			`">
            <button class="button primary fill" id="url-` +
			id +
			`">
                <h2>` +
			name +
			`</h2>
            </button>
        </div>`;

		return component;
	}
}

let expandable = new Expandable("scan-result");
expandable.create(jsonExample);
