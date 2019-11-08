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
			"episodes":[]
        },{
            "name": "Family Guy",
            "url": "some url",
			"id": "2",
			"episodes":[]
        },{
            "name": "Pulp Fiction",
            "id": "3",
            "url": "some url",
            "episodes":[]
        }]
    }
`;

let jsonExample2 = `
	{"scan-result": [{
		"name": "Season 1",
		"url": "some url",
		"id": "1",
		"episodes":[
			{
				"name": "Episode 1",
				"id": "1-ep-1",
				"url": "some url"
			},
			{
				"name": "Episode 2",
				"id": "1-ep-2",
				"url": "some url"
			},
			{
				"name": "Episode 3",
				"id": "1-ep-3",
				"url": "some url"
			}
		]
	},
	{
		"name": "Season 2",
		"url": "some url",
		"id": "2",
		"episodes":[
			{
				"name": "Episode 1",
				"id": "2-ep-1",
				"url": "some url"
			},
			{
				"name": "Episode 2",
				"id": "2-ep-2",
				"url": "some url"
			},
			{
				"name": "Episode 3",
				"id": "2-ep-3",
				"url": "some url"
			}
		]
	},
	{
		"name": "Season 3",
		"url": "some url",
		"id": "3",
		"episodes":[
			{
				"name": "Episode 1",
				"id": "3-ep-1",
				"url": "some url"
			},
			{
				"name": "Episode 2",
				"id": "3-ep-2",
				"url": "some url"
			},
			{
				"name": "Episode 3",
				"id": "3-ep-3",
				"url": "some url"
			}
		]
	}
]}
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

		$(this.selector).html("");
		for (let show of dataset[this.id]) {
			if (show["episodes"].length == 0) {
				this.injectShow(show);
			} else {
				this.injectSeason(show);
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

		$('#' + id).fadeOut(0, function() 
		{
			$('#' + id).fadeIn(this.animationTime);
		});
	}

	injectSeason(dataset) {
		let name = dataset["name"];
		let id = dataset["id"];

		//URL Element
		let urlElement = new URLElement("url-" + id, dataset["url"]);
		this.urlELements.push(urlElement);

		let component = this.createSeason(name, id);
		$(this.selector).append(component);

		this.injectEpisode(dataset["episodes"], id);

		$('#' + id).fadeOut(0, function() 
		{
			$('#' + id).fadeIn(this.animationTime);
		});
	}

	injectEpisode(dataset, containerId) {
		for (let i = 0; i < dataset.length; i++) {
			let episode = dataset[i];

			let name = episode["name"];
			let id = episode["id"];

			//URL Element
			let urlElement = new URLElement("url-" + id, episode["url"]);
			this.urlELements.push(urlElement);

			let component = this.createEpisode(name, id);
			$("#" + containerId + " .expandable").append(component);

			if (i + 1 == dataset.length) {
				$("#" + id).css("margin-bottom", "var(--border-size)");
			}
		}
	}

	createShow(name, id) {
		let component =
			`
        <div class="card card-action round"  id="` +id +`">
            <button class="button primary round-left" id="url-` +id +`">
                <h2>` +name +`</h2>
            </button>
        </div>`;
		return component;
	}

	createSeason(name, id) {
		let component =
			`
        <div class="expandable-card" id="` +id +`">
            <div class="card card-action round side-button">
                <button class="button primary fill-w round-left" id="exp-` +id +`">
					<h2>` +name +`</h2>
					<span class="icons">expand_more</span>
                </button>
			</div>
			<div class="expandable section-card"><div>
        </div>`;

		let expandableElement = new ExpandableElement(id, "expandable");
		this.expandableElements.push(expandableElement);
		return component;
	}

	createEpisode(name, id) {
		let component =
			`
        <div class="section-action terciary" id="` +id +`">
            <button class="button transparent fill" id="url-` +id +`">
                <h2>` + name +`</h2>
            </button>
        </div>`;

		return component;
	}
}

let expandable = new Expandable("scan-result");
expandable.create(jsonExample2);
