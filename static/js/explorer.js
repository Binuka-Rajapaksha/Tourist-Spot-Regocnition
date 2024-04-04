/*-----------------------------------*\
 * explorer.js
\*-----------------------------------*/

// Function to Upload Image
function ekUpload() {
  function Init() {
    console.log("Upload Initialised");

    var fileSelect = document.getElementById("file-upload"),
      fileDrag = document.getElementById("file-drag"),
      submitButton = document.getElementById("submit-button");

    fileSelect.addEventListener("change", fileSelectHandler, false);

    // Is XHR2 available?
    var xhr = new XMLHttpRequest();
    if (xhr.upload) {
      // File Drop
      fileDrag.addEventListener("dragover", fileDragHover, false);
      fileDrag.addEventListener("dragleave", fileDragHover, false);
      fileDrag.addEventListener("drop", fileSelectHandler, false);
    }
  }

  function fileDragHover(e) {
    var fileDrag = document.getElementById("file-drag");

    e.stopPropagation();
    e.preventDefault();

    fileDrag.className =
      e.type === "dragover" ? "hover" : "modal-body file-upload";
  }

  function fileSelectHandler(e) {
    // Fetch FileList object
    var files = e.target.files || e.dataTransfer.files;

    // Cancel event and hover styling
    fileDragHover(e);

    // Process all File objects
    for (var i = 0, f; (f = files[i]); i++) {
      parseFile(f);
      uploadFile(f);
    }
  }

  // Output
  function output(msg) {
    // Response
    var m = document.getElementById("messages");
    m.innerHTML = msg;
  }

  function parseFile(file) {
    console.log(file.name);
    output("<strong>" + encodeURI(file.name) + "</strong>");

    // var fileType = file.type;
    // console.log(fileType);
    var imageName = file.name;

    var isGood = /\.(?=gif|jpg|png|jpeg)/gi.test(imageName);
    if (isGood) {
      document.getElementById("start").classList.add("hidden");
      document.getElementById("response").classList.remove("hidden");
      document.getElementById("notimage").classList.add("hidden");
      // Thumbnail Preview
      document.getElementById("file-image").classList.remove("hidden");
      document.getElementById("file-image").src = URL.createObjectURL(file);
    } else {
      document.getElementById("file-image").classList.add("hidden");
      document.getElementById("notimage").classList.remove("hidden");
      document.getElementById("start").classList.remove("hidden");
      document.getElementById("response").classList.add("hidden");
      document.getElementById("file-upload-form").reset();
    }
  }

  function setProgressMaxValue(e) {
    var pBar = document.getElementById("file-progress");

    if (e.lengthComputable) {
      pBar.max = e.total;
    }
  }

  function updateFileProgress(e) {
    var pBar = document.getElementById("file-progress");

    if (e.lengthComputable) {
      pBar.value = e.loaded;
    }
  }

  function uploadFile(file) {
    var xhr = new XMLHttpRequest(),
      fileInput = document.getElementById("class-roster-file"),
      pBar = document.getElementById("file-progress"),
      fileSizeLimit = 1024; // In MB
    if (xhr.upload) {
      // Check if file is less than x MB
      if (file.size <= fileSizeLimit * 1024 * 1024) {
        // Progress bar
        pBar.style.display = "inline";
        xhr.upload.addEventListener("loadstart", setProgressMaxValue, false);
        xhr.upload.addEventListener("progress", updateFileProgress, false);

        // File received / failed
        xhr.onreadystatechange = function (e) {
          if (xhr.readyState == 4) {
            // Everything is good!
            // progress.className = (xhr.status == 200 ? "success" : "failure");
            // document.location.reload(true);
          }
        };

        // Start upload
        xhr.open(
          "POST",
          document.getElementById("file-upload-form").action,
          true
        );
        xhr.setRequestHeader("X-File-Name", file.name);
        xhr.setRequestHeader("X-File-Size", file.size);
        xhr.setRequestHeader("Content-Type", "multipart/form-data");
        xhr.send(file);
      } else {
        output("Please upload a smaller file (< " + fileSizeLimit + " MB).");
      }
    }
  }

  // Check for the various File API support.
  if (window.File && window.FileList && window.FileReader) {
    Init();
  } else {
    document.getElementById("file-drag").style.display = "none";
  }
}

ekUpload();

// Function to Close the Results Container
function closeResults() {
  document.getElementById("results-container").style.display = "none";
}

// Function to Process the Image
function processImage() {
  var resultText = "Colombo Municipal Council"; // Only for testing
  var inputElement = document.getElementById("file-upload");
  var file = inputElement.files[0];

  if (file) {
    var formData = new FormData();
    formData.append("image", file);

    fetch("/process_image", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        resultText = data.result; // Update resultText with the fetched result

        // Show the results container
        document.getElementById("resultText2").innerText = resultText;

        // Call searchPlaces with the updated resultText
        searchPlaces(resultText);

        // Show the results container
        document.getElementById("results-container").style.display = "block";

        // Auto-scroll to the results container
        document.getElementById("results-container").scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  } else {
    alert("Please choose an image before submitting.");
  }
}

// script.js
let map;
let marker;

// Keep track of the currently selected place ID
let selectedPlaceId;

// Initialize and Add the Map
function searchPlaces(place_name) {
  const keyword = place_name;

  // Check if a keyword is entered
  if (!keyword) {
    alert("Please enter a keyword");
    return;
  }

  // Google Maps Geocoding API
  const apiUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
    keyword
  )}&key=AIzaSyDNiDkCUEEDWpE0yY-yyhD71f0JA3Hoyk0`;

  // Fetch data from the API
  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      showLocationOnMap(data);
    })
    .catch((error) => console.error("Error fetching data:", error));
}

function showLocationOnMap(data) {
  selectedPlaceId = data.results[0].place_id;
  const location = data.results[0].geometry.location;

  // Create a new map if it doesn't exist
  map = new google.maps.Map(document.getElementById("map"), {
    center: location,
    zoom: 15,
  });

  // Add a marker for the location
  marker = new google.maps.Marker({
    position: location,
    map: map,
    title: data.results[0].formatted_address,
  });

  getPlaceDetails();
}

// Function to Get Place Details
function getPlaceDetails() {
  if (!selectedPlaceId) {
    alert("No place selected");
    return;
  }

  // Google Places (New) API for fetching place details
  const detailsUrl = `https://places.googleapis.com/v1/places/${selectedPlaceId}?fields=displayName,formattedAddress,nationalPhoneNumber,websiteUri,rating,reviews,editorialSummary&key=AIzaSyDNiDkCUEEDWpE0yY-yyhD71f0JA3Hoyk0`;

  // Fetch place details from the API
  fetch(detailsUrl)
    .then((response) => response.json())
    .then((placeDetails) => {
      displayPlaceDetails(placeDetails);
    })
    .catch((error) => console.error("Error fetching place details:", error));
}

// Function to Get Place Details
function displayPlaceDetails(placeDetails) {
  // Display detailed place information

  console.log("Place Details API Response:", placeDetails);

  const placeNameElement = document.getElementById("place-name");
  const formattedAddressElement = document.getElementById("address");
  const phoneNumberElement = document.getElementById("phone-number");
  const websiteElement = document.getElementById("website");
  const ratingElement = document.getElementById("rating");

  placeNameElement.innerText = placeDetails.displayName.text;
  formattedAddressElement.innerText = placeDetails.formattedAddress;
  phoneNumberElement.innerText = placeDetails.nationalPhoneNumber || "";
  websiteElement.href = placeDetails.websiteUri || "#";
  websiteElement.innerText = placeDetails.websiteUri || "";
  ratingElement.innerText = placeDetails.rating || "";
  const reviews = placeDetails.reviews || [];

  // Iterate over each review
  reviews.forEach((review) => {
    const reviewText = review.originalText.text;
    sendReviewToBackend(reviewText); // Send each review text to the backend
  });

  detailsContainer.appendChild(reviewsContainer);
}




// Function to Update Sentiment Animation
let number=document.getElementById('number');
let counter=0;
let sentimentScore=60;
let latetime=0

setInterval(()=>{
  if(counter==sentimentScore){
    clearInterval();
  }else{
    counter+=1;
    number.innerHTML=counter+'%';
  }
  updateSentimentAnimation();
  latetime=timeIntervals[sentimentScore];
},25)


function updateSentimentAnimation() {
   const newOffset = 530-(530*(sentimentScore/100));
   document.documentElement.style.setProperty('--dash-offset', newOffset);
}


function sendReviewToBackend(reviewText) {
  const requestBody = { text: reviewText };

  fetch('/reviews_sentiment', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
  })
  .then(response => response.json())
  .then(data => {
      updateProgressBar(data.positive, data.negative);
      updateLabels(data.positive, data.negative);
      console.log('Review sentiment analyzed successfully');
  })
  .catch(error => console.error('Error:', error));
}