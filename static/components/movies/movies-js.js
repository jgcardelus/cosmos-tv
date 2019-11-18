let openedAppsExample = `
    {
        "opened-apps": [
            {
                "show": "Netflix",
                "show-name": "Big Mouth",
                "id": "netflix-big-mouth"
            },
            {
                "show": "Prime",
                "show-name": "The Grand Tour",
                "id": "prime-the-grand-tour"
            },
            {
                "show": "YouTube",
                "show-name": "Cody Ko",
                "id": "youtube-cody-ko"
            }
        ]
    }
`

let openedAppsTest = `
    {
        "opened-apps": [
            {
                "show": "Netflix",
                "show-name": "Big Mouth",
                "id": "netflix-big-mouth-1"
            },
            {
                "show": "Prime",
                "show-name": "The Grand Tour",
                "id": "prime-the-grand-tour-1"
            },
            {
                "show": "YouTube",
                "show-name": "Cody Ko",
                "id": "youtube-cody-ko-1"
            }
        ]
    }
`

class OpenedApp
{
    constructor(id, parent)
    {
        this.id = id;
        this.parent = parent;
        this.isActive = false;
    }

    create()
    {
        this.events();
    }

    events()
    {
        $('#del-' + this.id).on('click', e =>
        {
            this.delete();
        });

        $('#act-' + this.id).on('click', e =>
        {
            this.activate();
        });
    }

    activate()
    {
        if (!this.isActive)
        {
            socket.emit('focus-app', this.id);
            this.parent.activateApp(this.id);
        }
    }

    delete()
    {
        socket.emit("close-app", this.id);
        this.parent.delete(this.id);
    }
}

class OpenedApps
{
    constructor()
    {
        this.openedApps = [];

        this.animationTime = 300;

        this.events();
    }

    events(){
        $('#close-opened-apps').on('click', e =>
        {
            if (this.openedApps.length > 0)
            {
                this.deleteAll();
            }
            else
            {
                raiseNotification("There are no open apps", SHORT);
            }
        });
    }

    addMDC(id)
    {
        let selectorPrefix = "#" + id;
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

    add(raw_dataset)
    {
        let dataset = JSON.parse(raw_dataset);
        let apps = dataset["opened-apps"];
        for (let app of apps)
        {
            this.injectApp(app);

            let openedApp = new OpenedApp(app["id"], this);
            openedApp.create();
            this.openedApps.push(openedApp);

            this.addMDC(app["id"]);
        }
        
    }

    update(raw_dataset)
    {
        let dataset = JSON.parse(raw_dataset);
        let app = dataset["opened-apps"][0];

        let id = app["id"];

        showName = app["show-name"];
        if (showName == undefined)
        {
            showName = "";
        }

        $('#' + id + ' .button h2').html(app["show"]);
        $('#' + id + ' .button p').html(showName);
    }

    create(raw_dataset)
    {
        if (this.openedApps.length == 0)
        {
            let dataset = JSON.parse(raw_dataset);
            let apps = dataset["opened-apps"];

            //Unbind events
            $('#opened-apps').unbind();

            this.injectAppContainer();
            for (let app of apps)
            {
                this.injectApp(app);

                let openedApp = new OpenedApp(app["id"], this);
                openedApp.create();
                this.openedApps.push(openedApp);

                this.addMDC(app["id"]);
            }
        }
        else
        {
            this.add(raw_dataset);
        }

        let last_element = this.openedApps.length - 1;
        let last_element_id = this.openedApps[last_element].id;

        this.activateApp(last_element_id);
    }

    deleteAll()
    {
        for(let i = 0; i < this.openedApps.length; i++)
        {
            let appId = this.openedApps[i].id;
            this.delete(appId);
        }
        socket.emit('close-all');
    }

    delete(id)
    {
        $('#' + id).slideUp(this.animationTime, () => {
            $('#' + id).remove();
        });

        for (let i = 0; i < this.openedApps.length; i++)
        {
            let openedApp = this.openedApps[i];
            if (openedApp.id == id)
            {
                this.openedApps.splice(i, 1);
                if (openedApp.isActive)
                {
                    if (this.openedApps.length >= 1)
                    {
                        let app = this.openedApps[0];
                        app.activate();
                    }
                }
                break;
            }
        }

        if (this.openedApps.length == 0)
        {
            this.deleteContainer();
        }
    }

    deleteContainer()
    {
        $('#opened-apps .card-container').slideUp(this.animationTime, () => {
            $('#opened-apps .card-container').remove();
        });

        $('#opened-apps .header').slideUp(this.animationTime, () => {
            $('#opened-apps .header').remove();
        });
    }

    injectAppContainer()
    {
        let component = this.createAppContainer();
        $('#opened-apps').html(component);
    }

    createAppContainer()
    {
        let component = `
            <h1 class="header">Opened apps</h1>
            <div class="card-container"></div>
        `;
        return component;
    }

    injectApp(app)
    {
        let component = this.createApp(app);
        $('#opened-apps .card-container').append(component);
        $('#' + app["id"]).slideUp(0);
        $('#' + app["id"]).slideDown(this.animationTime);
    }

    createApp(app)
    {
        let show = app["show"];
        let appId = app["id"];
        let showName = app["show-name"];

        if (showName == undefined)
        {
            showName = ""
        }

        let component = `
            <div class="card card-action side-button round" id="` + appId + `">
                <button class="button primary round-left" id="act-` + appId + `">
                    <h2>`+ show +`</h2>
                    <p class="padding-left">`+ showName +`</p>
                </button>
                <button class="button secondary round-right" id="del-` + appId + `">
                    <span class="icons">close</span>
                </button>
            </div>
        `;

        return component;
    }

    activateApp(id)
    {
        for (let i = 0; i < this.openedApps.length; i++)
        {
            if (this.openedApps[i].id != id)
            {
                this.openedApps[i].isActive = false;
                if ($('#'+ this.openedApps[i].id).hasClass('active-app'))
                {
                    $('#'+ this.openedApps[i].id).removeClass('active-app');
                }
            }
            else
            {
                this.openedApps[i].isActive = true;
                if (!$('#'+ this.openedApps[i].id).hasClass('active-app'))
                {
                    $('#'+ this.openedApps[i].id).addClass('active-app');
                }
            }
        }
    }
}

class App
{
    constructor(name, id, parent, searchPrefix, operator)
    {
        this.name = name;
        this.id = id;
        this.selector = '#' + id;
        this.parent = parent;
    
        this.searchPrefix = searchPrefix;
        this.operator = operator;

        this.requestedSearch = false;
    }

    create()
    {
        this.event();
    }

    event()
    {
        $(this.selector + ' .button.terciary').on('click', e => {
            this.startSearch();
        });

        $(this.selector + ' .button.primary').on('click', e => {
            this.start();
        });
    }

    start()
    {
        socket.emit('start-app', this.id);
        appTabs.change(1);
    }

    startSearch()
    {
        this.requestedSearch = true;
        $('#search-field').val("");
        searchPopup.activate();
    }

    search(request)
    {
        this.requestedSearch = false;
        let url = this.parseSearchRequest(request);
        socket.emit('start-app-search', this.id, url);
        appTabs.change(1);
    }

    parseSearchRequest(request)
    {
        let url = this.searchPrefix
        let words = request.split(' ');
        
        for (let i = 0; i < words.length; i++)
        {
            if(i < (words.length - 1))
            {
                url += words[i] + this.operator;
            }
            else
            {
                url += words[i];
            }
        }

        return url;
    }
}

class Apps{
    constructor()
    {
        this.apps = [];

        this.event();
    }

    event()
    {
        eventOn('search-request', request => {
            this.handleSearchRequest(request);
        })
    }

    handleSearchRequest(request)
    {
        for (let app of this.apps)
        {
            if (app.requestedSearch)
            {
                app.search(request);
                break;
            }
        }
    }

    create(raw_dataset)
    {
        let dataset = JSON.parse(raw_dataset);

        let apps = dataset["apps"];
        $('#apps .card-container').html("");
        for (let app of apps)
        {
            this.injectApp(app);
            let newApp = new App(app["name"], app["id"], this, app["search-prefix"], app["operator"]);
            newApp.create();
            this.apps.push(newApp);
        }

        this.addMDC('apps');
    }

    addMDC(id)
    {
        let selectorPrefix = "#" + id;
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

    injectApp(app)
    {
        let component = this.createApp(app);
        $('#apps .card-container').append(component);
    }

    createApp(app)
    {
        let name = app["name"];
        let id = app["id"];
        let component = `
            <div class="card card-action side-button round" id="` + id + `">
                <button class="button primary round-left">
                    <h2>`+ name +`</h2>
                </button>
                <button class="button terciary round-right">
                    <span class="icons">search</span>
                </button>
            </div>
        `;

        return component;
    }
}

let openedApps = new OpenedApps();
let apps = new Apps();

// BACKEND COMMUNICATION
socket.on('apps', data => {
    apps.create(data);
});

socket.on("opened-apps", data => {
    openedApps.create(data);
});

socket.on("opened-apps-update", data => {
    openedApps.update(data);
});