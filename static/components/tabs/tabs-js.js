/*
NAVBAR JS
*/

//CONFIG
const changeTime = 200;
const bounceTime = 75;
const swipeThreshold = 80;
const changeThreshold = 1 / 3;
const scrollingSoftener = 0.4;

class Tab {
    constructor(n, tabPage, tabButton) {
        this.n = n;
        this.tabPage = tabPage;
        this.tabButton = tabButton;
    }
}

class TabButton {
    constructor(n, id, elem) {
        this.n = n;
        this.id = id;
        this.elem = elem;

        $(this.elem).attr('tab-n', this.n);
    }

    activate() {
        if (!$(this.elem).hasClass('active-tab')) {
            $(this.elem).addClass('active-tab');
        }
    }

    deactivate() {
        if ($(this.elem).hasClass('active-tab')) {
            $(this.elem).removeClass('active-tab');
        }
    }
}

class TabPage {
    constructor(n, id, tabsContainer) {
        this.n = n;
        this.xpos = n * windowWidth;
        this.id = id;
        this.tabsContainer = tabsContainer;

        //this.relocateFab();
    }

    scroll(yDirection) {
        let selector = $(this.tabsContainer + ' .tabs .tab#' + this.id);
        let scrollPosition = selector.scrollTop();
        scrollPosition += yDirection;
        selector.scrollTop(scrollPosition);
    }

    relocateFab() {
        let fabSelector = $(this.tabsContainer + ' #' + this.id + ' .fab');
        if (fabSelector != null) {
            let left = 'calc(' + (this.n + 1) * 100 + 'vw - 4.5rem)';
            fabSelector.css('left', left);
        }
    }

    render(time, parent) {
        clearTimeout(parent.returnTimer);
        parent.ignoreScrolling = true;
        let n = this.n;
        let tabsContainer = this.tabsContainer;

        $(tabsContainer).animate({
            scrollLeft: (n * windowWidth)
        }, time, function() {
            parent.scrolledX = $(tabsContainer).scrollLeft();
            parent.ignoreScrolling = false;
            parent.actualTab = n;
            parent.trigger('page-change');
        });


        if (this.xpos != this.n * windowWidth) {
            this.xpos = this.n * windowWidth;
        }
    }

    change(parent) {
        this.render(changeTime, parent);
    }

    go(parent) {
        parent.ignoreScrolling = true;
        $(this.tabsContainer).scrollLeft((this.n * windowWidth));
        parent.scrolledX = $(this.tabsContainer).scrollLeft();
        parent.ignoreScrolling = false;
        parent.actualTab = this.n;
        parent.trigger('page-change');

        if (this.xpos != this.n * windowWidth) {
            this.xpos = this.n * windowWidth;
        }
    }

    bounce(parent) {
        this.render(bounceTime, parent);
    }
}

//PAGES AND TABS
class Tabs {
    constructor(initialTab, containerId, navbarId = null) {
        this.tabs = [];
        this.tabsSelector = '.tabs-container' + containerId;
        this.actualTab = initialTab;
        this.containerId = containerId;
        this.navbarId = navbarId;

        //SWIPPING AND SCROLLING
        this.allowPageChange = true;
        this.ignoreScrolling = false;
        this.returnTimer;
        this.scrolledX = 0;
        this.xPosStart = null;
        this.yPosStart = null;

        //EVENTS
        this.triggers = {};
    }

    create() {
        //Define page length
        let tabPages = $('.tabs-container' + this.containerId + ' .tabs .tab');
        let tabs = $('.tabs-container' + this.containerId + ' .tabs');
        tabs.css('width', tabPages.length * 100 + 'vw');
        //Define buttons
        let tabButtons = null;
        if (this.navbarId != null) {
            tabButtons = $('.navbar' + this.navbarId + ' .navbar-btn button');
            this.changeTabsHeight();
        }

        for (let i = 0; i < tabPages.length; i++) {
            let tabId = tabPages[i].id;
            let tabButton = null;
            if (this.navbarId != null) {
                tabButton = new TabButton(i, tabId, tabButtons[i]);
            }
            let tabPage = new TabPage(i, tabId, this.tabsSelector);

            let tab = new Tab(i, tabPage, tabButton);
            this.add(tab);
        }

        this.go(this.actualTab);
        this.addPageBehaviour();
    }

    changeTabsHeight() {
        let navbarHeight = $('.navbar' + this.navbarId).css('height');
        let minHeight = 'calc(100vh - ' + navbarHeight + ')';
        $(this.tabsSelector).css('min-height', minHeight);
    }

    addPageBehaviour() {
        //BUTTON BEHAVIOUR
        if (this.navbarId != null) {
            $('.navbar' + this.navbarId + ' .navbar-btn button').on('click', elem => {
                this.buttonClick(elem)
            });
        }

        //DESKTOP SCROLLING BEHAVIOUR
        $(this.tabsSelector).scroll(elem => {
            this.handleScroll(elem)
        });

        //SWIPING SCROLLING BEHAVIOUR
        document.querySelector(this.tabsSelector).addEventListener('touchstart', elem => {
            if (this.allowPageChange) {
                this.xPosStart = elem.changedTouches[0].pageX;
                this.yPosStart = elem.changedTouches[0].pageY;
            }
        });

        document.querySelector(this.tabsSelector).addEventListener('touchmove', elem => {
            if (this.allowPageChange) {
                elem.preventDefault();
                this.handleSwipe(elem)
            }
        });

        $(window).on('resize', elem => {
            this.change(this.actualTab);
        });
    }

    handleSwipe(element) {
        if (this.allowPageChange && !this.ignoreScrolling) {
            clearTimeout(this.returnTimer);

            let yPos = element.changedTouches[0].pageY;
            let yDirection = this.yPosStart - yPos;
            let xPos = element.changedTouches[0].pageX;
            let xDirection = this.xPosStart - xPos;
            if (Math.abs(xDirection) >= swipeThreshold) {
                if (xDirection > 0) {
                    this.next();
                } else {
                    this.prev();
                }
            } else {
                this.tabs[this.actualTab].tabPage.scroll(yDirection);
            }
        }
    }

    handleScroll(element) {
        clearTimeout(this.returnTimer);
        if (!this.ignoreScrolling) {
            let updatedSrollLeft = $(this.tabsSelector).scrollLeft();
            let deltaScroll = updatedSrollLeft - this.scrolledX;

            //The user has moved
            if (deltaScroll != 0) {
                let absDeltaScroll = Math.abs(deltaScroll);

                //To matain page sticking a timer will start, when it ends, it
                //will bounce back to the page it was
                let parent = this;
                this.returnTimer = setTimeout(function() {
                    if (absDeltaScroll <= (changeThreshold * windowWidth)) {
                        //If it is still in the page (calculated by the changeThreshold)
                        parent.ignoreScrolling = true;
                        //Bounce back
                        parent.bounce(parent.actualTab);
                    }
                }, 100);

                if (absDeltaScroll > (changeThreshold * windowWidth)) {
                    this.scrolledX = updatedSrollLeft;
                    if (deltaScroll > 0) {
                        this.next();
                    } else {
                        this.prev();
                    }
                }
            }
        }
    }

    prev() {
        if (this.actualTab - 1 >= 0) {
            this.actualTab--;
            this.change(this.actualTab);
        }
    }

    next() {
        if (this.actualTab + 1 < this.tabs.length) {
            this.actualTab++;
            this.change(this.actualTab);
        }
    }

    buttonClick(element) {
        this.actualTab = parseInt($(element.currentTarget).attr('tab-n'));
        this.change(this.actualTab);
    }

    add(tab) {
        this.tabs.push(tab);
    }

    activateFab(n) {
        for (let i = 0; i < this.tabs.length; i++) {
            let selector = $(this.tabsSelector + ' .tabs .tab#' + this.tabs[i].tabPage.id + ' .fab');
            if (selector != null) {
                let selectorSpan = $(this.tabsSelector + ' .tabs .tab#' + this.tabs[i].tabPage.id + ' .fab span');
                if (!selector.hasClass('hidden')) {
                    selector.addClass('hidden');
                    selectorSpan.addClass('hidden');
                }
            }
        }
        let fab = $(this.tabsSelector + ' .tabs .tab#' + this.tabs[n].tabPage.id + ' .fab');
        //Tab may not have fab
        if (fab != null) {
            let fabSpan = $(this.tabsSelector + ' .tabs .tab#' + this.tabs[n].tabPage.id + ' .fab span');
            fab.removeClass('hidden');
            fabSpan.removeClass('hidden');
        }
    }


    change(n) {
        if (this.navbarId != null)
        {
            for (let i = 0; i < this.tabs.length; i++) {
                this.tabs[i].tabButton.deactivate();
            }
        }

        let tab = this.tabs[n];
        this.activateFab(n);
        tab.tabPage.change(this);
        if (this.navbarId != null)
        {
            tab.tabButton.activate();
        }
    }

    bounce(n) {
        let tab = this.tabs[n];
        tab.tabPage.bounce(this);
    }

    go(n) {
        if (this.navbarId != null)
        {
            for (let i = 0; i < this.tabs.length; i++) {
                this.tabs[i].tabButton.deactivate();
            }
        }

        let tab = this.tabs[n];
        this.activateFab(n);
        tab.tabPage.go(this);
        if (this.navbarId != null)
        {
            tab.tabButton.activate();
        }
    }

    on(event, callback)
    {
        if (!this.triggers[event])
        {
            //Every event contains a list of actions that should be
            //called when it is triggered
            this.triggers[event] = [];
        }

        //Add the event that must be triggered
        this.triggers[event].push(callback);
    }

    trigger(event, params)
    {
        if(this.triggers[event])
        {
            for (let i = 0; i < this.triggers[event].length; i++)
            {
                //Execute every callback in the event
                this.triggers[event][i](params);
            }
        }
    }
}
