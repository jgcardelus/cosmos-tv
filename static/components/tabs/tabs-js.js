/*
NAVBAR JS
*/

//CONFIG
const changeTime = 200;
const bounceTime = 75;
const swipeThreshold = 80;
const changeThreshold = 1/3;

let actualPage = 1;

//SCROLLING BEHAVIOUR
let ignoreScrolling = false;
let scrolledX = $("#app-container").scrollLeft();
let returnTimer;

//SWIPING OVERRIDE
let touchStart = null;
document.querySelector("#app-container").addEventListener('touchstart', function(e)
{
	touchStart = e.changedTouches[0].pageX;
});

document.querySelector("#app-container").addEventListener('touchmove', function(e)
{
	e.preventDefault();
	handleTouchmove(e.changedTouches[0].pageX);
});

function handleTouchmove(yPos)
{
	if(!ignoreScrolling)
	{
		let direction = touchStart - yPos;
		if (Math.abs(direction) >= swipeThreshold)
		{
			if (direction > 0)
			{
				if(actualPage + 1 < pages.pages.length)
				{
					actualPage++;
					pages.change(actualPage);
				}
			}
			else
			{
				if (actualPage - 1 >= 0)
				{
					actualPage--;
					pages.change(actualPage);
				}
			}
		}
	}	
}

//DESKTOP SCROLLING BEHAVIOUR
$("#app-container").scroll(function()
{
	clearTimeout(returnTimer);
	if(!ignoreScrolling)
	{
		let updatedSrollLeft = $("#app-container").scrollLeft();
		let deltaScroll = updatedSrollLeft - scrolledX;

		if (deltaScroll != 0)
		{
			let absDeltaScroll = Math.abs(deltaScroll);
			
			returnTimer = setTimeout(function()
			{
				if(absDeltaScroll <= (changeThreshold * windowWidth))
				{
					ignoreScrolling = true;
					pages.bounce(actualPage);
				}
			}, 100);
			
			if (absDeltaScroll > (changeThreshold * windowWidth))
			{
				scrolledX = updatedSrollLeft;
				if (deltaScroll > 0)
				{
					if(actualPage + 1 < pages.pages.length)
					{
						actualPage++;
						pages.change(actualPage);
					}
				}
				else
				{
					if (actualPage - 1 >= 0)
					{
						actualPage--;
						pages.change(actualPage);
					}
				}
			}
		}
	}
});

//PAGES AND TABS
class Pages
{
	constructor()
	{
		this.pages = [];
	}

	add(page)
	{
		this.pages.push(page);
	}

	change(n)
	{
		for (let i = 0; i < this.pages.length; i++)
		{
			this.pages[i].button.deactivate();
		}

		let page = this.pages[n];
		page.tab.change();
		page.button.activate();
	}

	bounce(n)
	{
		let page = this.pages[n];
		page.tab.bounce();
	}

	go(n)
	{
		for (let i = 0; i < this.pages.length; i++)
		{
			this.pages[i].button.deactivate();
		}

		let page = this.pages[n];
		page.tab.change();
		page.button.activate();
	}
}

class Page
{
	constructor(n, tab, button)
	{
		this.n = n;
		this.tab = tab;
		this.button = button;
	}
}

class PageButton
{
	constructor(n, id, elem)
	{
		this.n = n;
		this.id = id;
		this.elem = elem;

		$(this.elem).attr('page-n', this.n);
	}

	activate()
	{
		if(!$(this.elem).hasClass('activePage'))
		{
			$(this.elem).addClass('activePage');
		}
	}

	deactivate()
	{
		if($(this.elem).hasClass('activePage'))
		{
			$(this.elem).removeClass('activePage');
		}
	}
}

class PageTab
{
	constructor(n, id)
	{
		this.n = n;
		console.log(this.n);
		this.xpos = n * windowWidth;
		this.id = id;
	}

	render(time)
	{
		clearTimeout(returnTimer);
		ignoreScrolling = true;
		let n = this.n;
		$('#app-container').animate({
			scrollLeft: (n * windowWidth)
		}, time, function() {
			scrolledX = $("#app-container").scrollLeft();
			ignoreScrolling = false;
		});

		if (this.xpos != this.n * windowWidth)
		{
			this.xpos = this.n * windowWidth;
		}
	}

	change()
	{
		this.render(changeTime);
	}

	go()
	{
		this.render(0);
	}

	bounce()
	{
		this.render(bounceTime);
	}
}

//CREATE PAGES AND DEFINE CSS
let pageButtonsDom = $('#navbar .navbar-btn button');
$('#app-container #app').css('width', pageButtonsDom.length * 100 + 'vw');
let pageTabsDom = $('#app-container #app .pageTab');

let pages = new Pages();

for (let i = 0; i < pageButtonsDom.length; i++)
{
	let pageId = pageTabsDom[i].id;
	let pageButton = new PageButton(i, pageId, pageButtonsDom[i]);
	let pageTab = new PageTab(i, pageId);

	let page = new Page(i, pageTab, pageButton);
	pages.add(page);
}

pages.go(actualPage);

//BUTTON BEHAVIOUR
$('.navbar-btn button').on('click', function()
{
	actualPage = parseInt($(this).attr('page-n'));
	pages.change(actualPage);
});