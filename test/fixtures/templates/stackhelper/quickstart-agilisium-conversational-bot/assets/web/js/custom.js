/* Start declaring global variables */
// lexRuntTime will be intialized during document ready.
var lexRunTime = "";
// Variable to hold bot alias and bot name.
// It will be intialized during document ready.
var botAlias = "";
var botName = "";
// For simplicity we set the user id as follows.
// For multiple user application switch to different strategy.
var lexUserId = "chatInput-demo" + Date.now();
// Variable to hold session infromation from Lex.
var sessionAttributes = {};
// Loader icon HTML holder. It will be used while waiting for
// the response from Lex. Intialized during init bot.
var loaderElement = "";
/* End declaring global variables */

// Function to send user statement to the Lex and get reponse.
function pushChat() {
	// User statement is read directly form the input box itself.
	var chatInputText = document.getElementById('chatInput');
	// Disable mic tempropily and dim mic icon.
	micEnabled = false;
	$(".mic-con").css('opacity', '0.25');
	// Checks is there such element with id chatInput and it
	// contains any value and its length greater than 0 after triming.
	if(chatInputText && chatInputText.value && chatInputText.value.trim().length > 0) {
		// Trim spaces from the input and update visual cues for
		// the user. Disable the chat input temprorily.
		var chatInput = chatInputText.value.trim();
		chatInputText.value = 'Lisa is typing...';
		chatInputText.locked = true;
		document.getElementById("chatInput").disabled = true;

		// Create a parameter dict with bot details and user
		// details. It will be used during the negotiation with
		// the Lex.
		var params = {
			botAlias: botAlias,
			botName: botName,
			inputText: chatInput,
			userId: lexUserId,
			sessionAttributes: {}
		};
		// Append the user statement to the chat window.
		showRequest(chatInput);
		// Append the loader element to view loading icon and
		// scroll to bottom.
		$("#chat-con").append(loaderElement);
		$("#conversation").scrollTop($("#chat-con").height());
		// Post the user statements to Lex and wait for the response.
		lexRunTime.postText(params, function(err, data) {
			// Received response from the Lex so, enalbe mic back and
			// remove the loader icon from the chat window.
			micEnabled = true;
			$(".mic-con").css('opacity', '1');
			$(".loader-con").remove();

			// If error is received then log it to the console and
			// show the error message in the chat window.
			if(err) {
				console.log(err, err.stack);
				showError('Error:  ' + err.message + ' (see console for details)')
			}
			// If data is received then copy the session attributes from
			// the response to the global variable, so it can be consumed
			// by other functions. Show the received response to the user.
			if(data) {
				sessionAttributes = data.sessionAttributes;
				console.log(data);
				showResponse(data);
			}
			// Set the user input box to empty, enable it and
			// focus it, so user can start typing without clicking
			// the text box again.
			chatInputText.value = '';
			chatInputText.locked = false;
			document.getElementById("chatInput").disabled = false;
			document.getElementById("chatInput").focus();
		});
	}
}

// Function showRequest takes the user input message and add markups
// around it to display it in the chat window.
function showRequest(inputText) {
	// Prepare a container div to hold the request message
	var request = document.createElement("div");
	// The following class names have some styles associated with
	// them so update the custom.css file in the styles folder if
	// you want to change this class name.
	request.className = 'usr-conver-con';
	// Markup to add the user image to the chat window.
	userImage = '<div class="usr-img-con"><img src="images/human.png" alt="" width="40px"></div>';
	// Markup to hold the user request messge.
	userMsg = '<div class="usr-conver-text">' + inputText + '</div>';
	// Merge the user image and request message markups and append it
	// to the chat window.
	request.innerHTML = userImage + userMsg;
	$("#chat-con").append(request);
	// Scrolls to bottom of the chat window.
	$("#conversation").scrollTop($("#chat-con").height());
}

// Function showError takes the error message and add markups
// around it to display it in the chat window.
function showError(errorMsg) {
	// Prepare a container div to hold the error message
	var error = document.createElement("div");
	// The following class names have some styles associated with
	// them so update the custom.css file in the styles folder if
	// you want to change this class name.
	error.className = 'usr-conver-con';
	// Markup to add the bot image to the chat window.
	botImage = '<div class="bot-img-con"><img src="images/bot.png" alt="" width="40px"></div>';
	// Markup to hold the error messge.
	botMsg = '<div class="bot-conver-text">' + "Sorry something went wrong!" + '</div>';
	// Merge the bot image and error message markups and append it
	// to the chat window.
	error.innerHTML = botImage + botMsg;
	$("#chat-con").append(error);
	// Scrolls to bottom of the chat window.
	$("#conversation").scrollTop($("#chat-con").height());
}

// Function showResponse takes the response message and add markups
// around it to display it in the chat window. Additionally it adds
// markups for tables if present.
function showResponse(lexResponse) {
	// Prepare a container div to hold the reponse message
	var response = document.createElement("div");
	// The following class names have some styles associated with
	// them so update the custom.css file in the styles folder if
	// you want to change this class name.
	response.className = 'bot-conver-con';
	resTable = "";

	// Checks whether response contains table. Table data are passed
	// as string in the card attribute of session attributes.
	if(lexResponse.sessionAttributes && lexResponse.sessionAttributes.card && lexResponse.intentName) {
		// In Lex session attributes only support string as value.
		// So table data is passed as json encoded string. Parse it
		// to get the actual table data json.
		card = JSON.parse(lexResponse.sessionAttributes.card);
		// Variables intialized to default values and will be used
		// down the line.
		table = "";
		resTable = "";
		rightAlign = false;
		rightAlignIndex = 0;

		if(card.table) {
			table = card.table;

			// Adding table markups
			resTable = "<table><tbody><tr>";
			// Loop to add headers to the table
			for(index in table) {
				i = 0;
				for(item in table[index]) {
					// In order to right aling number column in the table we are
					// checking the column names for orders, revenue or sales
					// team size. If matches then remembering the column position
					// to add the necessary markup later.
					// Note : So far the solution uses numbers in these columns only,
					// so I added a simple if statement here. If you extend then change
					// the logic to something else.
					// Also it is assumed only on column will contain number values.
					// If you need support for additional columns please extend this logic
					// accordingly.
					if(item.toLowerCase() == "orders" || item.toLowerCase() == "revenue" || item.toLowerCase() == "sales team size") {
						rightAlign = true;
						rightAlignIndex = i;
					}
					// Markup to add the actual headers. Note, the header is
					// actually the key of the respective data elements.
					// To see what it actually means see the console for the
					// data returned by the backend lambda.
					resTable += '<th class="center-align">' + item + "</th>";
					i++;
				}
				// Once first row of the table is processed break the loop.
				break;
			}

			// Closes the header row markup.
			resTable += "</tr>";
		}
		// If help is sent in the card rather table of data, intialize
		// some special markups to style it.
		else if(card.help) {
			table = card.help;

			resTable = '<div class="help-con">';
		}

		// Loop to fill the data part of the table or the help contents
		for(index in table) {
			// If table data has to be filled
			if(card.table) {
				// Add the table row markup and specially treats the total row
				// at the end of the table to add some class to it, so that
				// it can be styled as needed in our style sheet.
				resTable += "<tr" + (Object.values(table[index])[0].toLowerCase() == "total" ? ' class="total-row"' : "") + ">";
				// Variable to track the current column number.
				i = 0;
				// Loop to process individual cell elements of the current row.
				for(item in table[index]) {
					// Add the table data markup and checks whether the data has
					// to be right aligne, if so adds some class attributes so that
					// it can be right aligned in CSS.
					resTable += "<td" + (rightAlign && (rightAlignIndex == i) ? ' class="right-align"' : "") + ">" + table[index][item] + "</td>";
					// Increment the current coumn number tracker.
					i++;
				}
				// Markup to close the current data row in the table.
				resTable += "</tr>";
			}
			// If help statements has to be filled
			else if(card.help) {
				// The following statement contains some class attributes, please
				// don't change them as they as associated with some style properties and
				// click triggers. The user can click the individual element to
				// send it to the Lex directly without re typing it.
				resTable += '<div class="help-item-con"><div class="help-item">' + table[index] + "</div></div>";
			}
		}

		// Markup to end table, if response is a table.
		if(card.table) {
			resTable += "</tbody></table>";
		}
		// Markup to end help, if response contains list of help statements.
		else if(card.help) {
			resTable += "</div>";
		}
	}

	// Checks is there any text response.
	if(lexResponse.message) {
		// Markup to add bot image to the response.
		botImage = '<div class="bot-img-con"><img src="images/bot.png" alt="" width="40px"></div>';
		// If reponse contains data table or help statements then append the
		// the above processed markups after the user text message.
		if(resTable) {
			botMsg = '<div class="bot-conver-text">' + lexResponse.message + "<br>" + resTable + '</div>';
		}
		// If user response is just text message, then just add the markups to it.
		else {
			botMsg = '<div class="bot-conver-text">' + lexResponse.message + '</div>';
		}
		// Combine the bot image and bot message markups respectively.
		response.innerHTML = botImage + botMsg;
	}

	// Apped the bot response to the chat window and scroll to
	// bottom of the chat window.
	$("#chat-con").append(response);
	$("#conversation").scrollTop($("#chat-con").height());
}

// Setter funtion for user statement.
function setInput(text) {
    $("#chatInput").val(text);
}

// Getter funtion for user statement.
function getInput(text) {
    return $("#chatInput").val();
}

// Function to initialize the chat window with some
// predefined message from bot, that you see when
// the page is loaded.
function initBot() {
	var response = document.createElement("div");
	response.className = 'bot-conver-con';
	botImage = '<div class="bot-img-con"><img src="images/bot.png" alt="" width="40px"></div>';
	botMsg = '<div class="bot-conver-text">I am Lisa, your BI Chatbot. I can help you with sales performance insights of our company.<br/><br/>This is a demo solution, so my scope of conversation is limited. Please ask for "help" to know the list of metrics I can answer.</div>';
	var loader = document.createElement("div");
	loader.className = 'loader-con';
	loaderElement = '<div class="loader-con"><img id="loader" src="images/loader.gif" width="25"></div>';
	response.innerHTML = botImage + botMsg;
	$("#chat-con").append(response);
	$("#conversation").scrollTop($("#chat-con").height());
}

// Handler to receive the keypress event of the chat input
// text box.
$("#chatInput").on('keypress', function(e) {
	// If enter key is pressed then send the content of the
	// user statement to Lex.
	if(e.keyCode == 13) {
		pushChat();
	}
});

$(document).ready(function() {
	// Handler to process click event from the help statements.
	// These statements are dynamically added so the handler
	// function is defined in different notation.
	$(".chatbot").on("click", ".help-item", function(event) {
		event.preventDefault();
		// Whatever statement is clicked send it to Lex as it is.
		$("#chatInput").val(event.target.innerHTML);
		pushChat();
	});

	// This will load the configs from the config.json file
	// present at the root directory. It includes bot name,
	// bot alias, region, and cognito pool id.
	$.get('config.json', function(data) {
		// Don't remove the following line, sometime the
		// data object is not automatically parsed.
		if(Object.prototype.toString.call(data) === "[object String]") {
			data = JSON.parse(data);
		}
		botAlias = data.botAlias;
		botName = data.botName;

		// Connect to cognito as unauthenticated identity and
		// get the credentials to invoke lex services.
		AWS.config.region = data.region;
		AWS.config.credentials = new AWS.CognitoIdentityCredentials({
			IdentityPoolId: data.poolId,
		});

		// Based on the above credentials create a lex run time
		// object and assign it to the global variable.
		lexRunTime = new AWS.LexRuntime();
	});

	// To handle the get started button click event.
	// When clicked it takes you to the Agilisium website.
	$(".get-started-button").on("click", function() {
		window.location = "https://www.agilisium.com/solutions/bi-conversational-bot/"
	});
});

// Initialize the chat window with some message from bot.
initBot();