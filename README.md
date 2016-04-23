# Safe-Ride-App


# Overview

A web-based application that will assist Safe Ride in performing its duties. 
Built with Python, Flask, mongoDB, Javascript (utilizing AJAX JSON requests for live updates), and HTML5+CSS3 (on bootstrap)

Safe-Ride-App is live at http://ix.cs.uoregon.edu:6066
(Please let me know if you want to see it and I will fire up the application)

# How it Works

When a user sends a request to load the url, the app routes that user to the ride request page, the customer-facing portion of the app. 
In this page, users complete a form whose fields form a rideRequest object. Upon submission, the app checks user input fields to
determine whether the information is adequete to form a ride request. If it is, the values from the completed fields are bundled and
sent from Javascript to Python as a JSON object. The information is then processed into the database. The ride is rebuilt within the 
dispatcher view, which can only be accesed via url token parameters username and password. A manage page is used by an admin to create
and delete dispatch accounts.

<b>NOTE</b> There are several python files to assist with testing (printing and clearing specific components )

Please contact me with any other suggestions or questions you have regarding this project! igarrett@uoregon.edu
