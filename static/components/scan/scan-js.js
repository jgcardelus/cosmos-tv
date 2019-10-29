//DEFINING PAGE
let scanTabs = new Tabs(0, '#scan');
scanTabs.create();
tabs.push(scanTabs);

//PAGE ACTIVATION AND DEACTIVATION
function activateScan()
{
    for (let i = 0; i < tabs.length; i++)
    {
        let tab = tabs[i];
        if (tab != scanTabs)
        {
            tab.allowPageChange = false;
        }
    }
    scanTabs.allowPageChange = true;
    $('#scan').css('z-index', '500');
    $('#scan tabs').css('z-index', '500');
    if ($('#scan').hasClass('hidden'))
    {
        $('#scan').removeClass('hidden');
    }
    scanTabs.change(1);
}

function deactivateScan()
{
    $('#scan').css('z-index', '0');
    $('#scan tabs').css('z-index', '0');
    for (let i = 0; i < tabs.length; i++)
    {
        let tab = tabs[i];
        tab.allowPageChange = false;
    }
    appTabs.allowPageChange = true;
    if (!$('#scan').hasClass('hidden'))
    {
        $('#scan').addClass('hidden');
    }
}

let hasChanged = false;
scanTabs.on('page-change', () => {
    if (scanTabs.actualTab == 0)
    {
        if (hasChanged)
        {
            deactivateScan();
            hasChanged = false;
        }
    }
    else if(scanTabs.actualTab == 1)
    {
        hasChanged = true;
    }
});

$('#close-span').on('click', () =>{
    scanTabs.change(0);
})

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
`

let a = JSON.parse(jsonExample);

class Expandable{
    constructor(id)
    {
        this.id = id;
        this.selector = '.card-container#' + id;
        this.dataset = null;
        this.parsedHTML = '';

        this.expandIcon = "expand_more";
        this.contractIcon = "expand_less";
    }

    load(raw_dataset)
    {
        let dataset = JSON.parse(raw_dataset);
        this.dataset = dataset;
        this.parsedHTML = '';

        //Clear html
        $(this.selector).html('');
        for (let show of dataset[this.id])
        {
            if (show["seasons"].length == 0)
            {
                this.injectShow(show);
            }
            else
            {
                this.injectExpandableShow(show);
            }
        }
    }

    injectShow(dataset)
    {
        let name = dataset["name"];
        let id = dataset["id"];
        let component = this.createShow(name, id)
        $(this.selector).append(component);
    }

    injectExpandableShow(dataset)
    {
        let name = dataset["name"];
        let id = dataset["id"];
        let component = this.createExpandableShow(name, id);
        $(this.selector).append(component);

        this.injectSeason(dataset["seasons"], id);
    }

    injectSeason(dataset, containerId)
    {
        for (let season of dataset)
        {
            let name = season["name"];
            let id = season["id"];
            let component = this.createSeason(name, id);
            $('#' + containerId).append(component);

            this.injectEpisode(season["episodes"], id);
        }
    }

    injectEpisode(dataset, containerId)
    {
        for (let episode of dataset)
        {
            let name = episode["name"];
            let id = episode["id"];
            let component = this.createEpisode(name, id);
            console.log(component);
            $('#' + containerId).append(component);
        }
    }

    createShow(name, id)
    {
        let component = `
        <div class="card card-action round">
            <button class="button primary round-left" id="`+ id +`">
                <h2>`+ name +`</h2>
            </button>
        </div>`;
        return component;
    }

    createExpandableShow(name, id)
    {
        let component = `
        <div class="expandable-card" id="`+ id +`">
            <div class="card card-action side-button round">
                <button class="button primary round-left">
                    <h2>`+ name +`</h2>
                </button>
                <button class="button secondary round-right">
                    <span class="icons">expand_more</span>
                </button>
            </div>
        </div>`;

        return component;
    }

    createSeason(name, id)
    {
        let component = `
        <div class="expandable section-card" id="`+ id +`">
            <div class="section-header side-button">
                <button class="button transparent">
                    <h2>`+name+`</h2>
                    <span class="icons">expand_more</span>
                </button>
            </div>
        </div>`;

        return component;
    }

    createEpisode(name, id)
    {
        let component = `
        <div class="section-action" id="`+id+`">
            <button class="button primary fill">
                <h2>`+name+`</h2>
            </button>
        </div>`;

        return component;
    }
}

let expandable = new Expandable('scan-result');
