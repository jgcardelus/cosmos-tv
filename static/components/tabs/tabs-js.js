/*
NAVBAR JS
*/

//CONFIG
const changeTime = 200;
const bounceTime = 75;
const swipeThreshold = 80;
const changeThreshold = 1/3;

class Tab
{
	constructor(n, tabPage, tabButton)
	{
		this.n = n;
		this.tabPage = tabPage;
		this.tabButton = tabButton;
	}
}

class TabButton
{
	constructor(n, id, elem)
	{
		this.n = n;
		this.id = id;
		this.elem = elem;

		$(this.elem).attr('tab-n', this.n);
	}

	activate()
	{
		if(!$(this.elem).hasClass('activeTab'))
		{
			$(this.elem).addClass('activeTab');
		}
	}

	deactivate()
	{
		if($(this.elem).hasClass('activeTab'))
		{
			$(this.elem).removeClass('activeTab');
		}
	}
}

class TabPage
{
	constructor(n, id, tabsContainer)
	{
		this.n = n;
		this.xpos = n * windowWidth;
		this.id = id;
		this.tabsContainer = tabsContainer;

		this.relocateFab();
	}

	relocateFab()
	{
		let fabSelector = $(this.tabsContainer + ' #' + this.id + ' .fab');
		if(fabSelector != null)
		{
			let left = 'calc(' + (this.n + 1) * 100 + 'vw - 4.5rem)';
			fabSelector.css('left', left);
		}
	}

	render(time, parent)
	{
		clearTimeout(parent.returnTimer);
		parent.ignoreScrolling = true;
		let n = this.n;
		let tabsContainer = this.tabsContainer;

		$(tabsContainer).animate({
			scrollLeft: (n * windowWidth)
		}, time, function() {
			parent.scrolledX = $(tabsContainer).scrollLeft();
			parent.ignoreScrolling = false;
		});


		if (this.xpos != this.n * windowWidth)
		{
			this.xpos = this.n * windowWidth;
		}
	}

	change(parent)
	{
		this.render(changeTime, parent);
	}

	go(parent)
	{
		parent.ignoreScrolling = true;
		$(this.tabsContainer).scrollLeft((this.n * windowWidth));
		parent.scrolledX = $(this.tabsContainer).scrollLeft();
		parent.ignoreScrolling = false;

		if (this.xpos != this.n * windowWidth)
		{
			this.xpos = this.n * windowWidth;
		}
	}

	bounce(parent)
	{
		this.render(bounceTime, parent);
	}
}

//PAGES AND TABS
class Tabs
{
	constructor(initialTab, containerId, navbarId=null)
	{
		this.tabs = [];
		this.tabsContainer = '.tabs-container' + containerId;
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
	}

	create()
	{
		//Define page length
		let tabPages = $('.tabs-container' + this.containerId + ' .tabs .tab');
		let tabs = $('.tabs-container' + this.containerId + ' .tabs');
		tabs.css('width', tabPages.length * 100 + 'vw');
		//Define buttons
		let tabButtons = null;
		if (this.navbarId != null)
		{
			tabButtons = $('.navbar' + this.navbarId + ' .navbar-btn button');
			this.changeTabsHeight();
		}

		for (let i = 0; i < tabPages.length; i++)
		{
			let tabId = tabPages[i].id;
			let tabButton = null;
			if (this.navbarId != null)
			{
				tabButton = new TabButton(i, tabId, tabButtons[i]);
			}
			let tabPage = new TabPage(i, tabId, this.tabsContainer);

			let tab = new Tab(i, tabPage, tabButton);
			this.add(tab);
		}

		this.go(this.actualTab);
		this.addPageBehaviour();
	}

	changeTabsHeight()
	{
		let navbarHeight = $('.navbar' + this.navbarId).css('height');
		let minHeight = 'calc(100vh - ' + navbarHeight +')';
		$(this.tabsContainer).css('min-height', minHeight);
		$(this.tabsContainer + ' .tabs .tab').css('min-height', 'calc(100vh + 4.125rem)');
	}

	addPageBehaviour()
	{
		//BUTTON BEHAVIOUR
		if (this.navbarId != null)
		{
			$('.navbar' + this.navbarId + ' .navbar-btn button').on('click', elem => {this.buttonClick(elem)});
		}

		//DESKTOP SCROLLING BEHAVIOUR
		$(this.tabsContainer).scroll(elem => {this.handleScroll(elem)});

		//SWIPING SCROLLING BEHAVIOUR
		document.querySelector(this.tabsContainer).addEventListener('touchstart', elem => {
			if(this.allowPageChange)
			{
				this.xPosStart = elem.changedTouches[0].pageX;
				this.yPosStart = elem.changedTouches[0].pageY;
			}
		});

		document.querySelector(this.tabsContainer).addEventListener('touchmove', elem => {
			if (this.allowPageChange)
			{
				elem.preventDefault();
				this.handleSwipe(elem)
			}
		});

		$(window).on('resize', elem =>
		{
			this.change(this.actualTab);
		});
	}

	handleSwipe(element)
	{
		if (this.allowPageChange && !this.ignoreScrolling)
		{
			clearTimeout(this.returnTimer);

			let yPos = element.changedTouches[0].pageY;
			let yDirection = this.yPosStart - yPos;
			let xPos = element.changedTouches[0].pageX;
			let xDirection = this.xPosStart - xPos;
			if (Math.abs(xDirection) >= swipeThreshold)
			{
				if (xDirection > 0)
				{
					this.next();
				}
				else
				{
					this.prev();
				}
			}
			else {
				let actualYPos = $(window).scrollTop();
				actualYPos += yDirection;
				$(window).scrollTop(actualYPos);
			}
		}
	}

	handleScroll(element)
	{
		clearTimeout(this.returnTimer);
		if(!this.ignoreScrolling)
		{
			let updatedSrollLeft = $(this.tabsContainer).scrollLeft();
			let deltaScroll = updatedSrollLeft - this.scrolledX;

			//The user has moved
			if (deltaScroll != 0)
			{
				let absDeltaScroll = Math.abs(deltaScroll);

				//To matain page sticking a timer will start, when it ends, it
				//will bounce back to the page it was
				let parent = this;
				this.returnTimer = setTimeout(function()
				{
					if(absDeltaScroll <= (changeThreshold * windowWidth))
					{
						//If it is still in the page (calculated by the changeThreshold)
						parent.ignoreScrolling = true;
						//Bounce back
						parent.bounce(parent.actualTab);
					}
				}, 100);

				if (absDeltaScroll > (changeThreshold * windowWidth))
				{
					this.scrolledX = updatedSrollLeft;
					if (deltaScroll > 0)
					{
						this.next();
					}
					else
					{
						this.prev();
					}
				}
			}
		}
	}

	prev()
	{
		if (this.actualTab - 1 >= 0)
		{
			this.actualTab--;
			this.change(this.actualTab);
		}
	}

	next()
	{
		if(this.actualTab + 1 < this.tabs.length)
		{
			this.actualTab++;
			this.change(this.actualTab);
		}
	}

	buttonClick(element)
	{
		this.actualTab = parseInt($(element.currentTarget).attr('tab-n'));
		this.change(this.actualTab);
	}

	add(tab)
	{
		this.tabs.push(tab);
	}

	change(n)
	{
		for (let i = 0; i < this.tabs.length; i++)
		{
			this.tabs[i].tabButton.deactivate();
		}

		let tab = this.tabs[n];
		tab.tabPage.change(this);
		tab.tabButton.activate();
	}

	bounce(n)
	{
		let tab = this.tabs[n];
		tab.tabPage.bounce(this);
	}

	go(n)
	{
		for (let i = 0; i < this.tabs.length; i++)
		{
			this.tabs[i].tabButton.deactivate();
		}

		let tab = this.tabs[n];
		tab.tabPage.go(this);
		tab.tabButton.activate();
	}
}
