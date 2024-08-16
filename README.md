# DSC 2024

This is the course about [Data Science and Communication in Smart Cities](https://web.ntnu.edu.tw/~cw/icoil/) in NTNU.

## Projects

Project Topic: Commute Convoying

- Objective: Providing safer commute routes for children and/or elders
- Requirements:
  - Data Science: commute route recommendation, traffic and volunteer information
  - Data communication: traveller location reporting; patroller recruiting
- Analysis of challenges and issues
- Proof-of-concept prototype implmenetation

Prototype:

- Using Google Maps to get the route.
- Calculate the weight of each coordinates provided by the route with the sidewalk width and the traffic accidents.
- Using OSM to find the new route.
- Convert the OSM route to Google Maps' route.

Challenges:

- The weight calculation should be more precised based on other datasets other than accidents and sidewalk width.
- Improvement of data quality.
