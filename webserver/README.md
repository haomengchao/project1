#W4111 project1: online medical app
Team menbers： Mengchao Hao, Jiyuan Yang
UNI: mh3884, jy2930
##Setup:
###Install libraries:
    pip install click, flask, sqlalchemy
###Run it:
    python server.py
##Usage:
The server runs on http://0.0.0.0:8111/.
###Sign up:
Go to the register page. You can choose a user as doctor or patient.
###Log in:
Use the account you signed up to log in.
###Functions:
1. See your own homepage: click the link of your username. If you are a patient, then you can see all the posts you made and illnesses about you. If you are a doctor, then you can also see the posts and the cure information.
2. See all the posts: Click "posts" to see all the posts, and click "make a post" to make a new post.
3. Ratings: Click the link to see all the ratings of all doctors, you can also see the specific ratings of a certain doctor by using the search function at the bottom of rating page.
4. Add illness and cure: If you are a docter then you can add illness and cure information. Of course the attending physician of that illness or cure is you.
5. Add rating: If you are a patient then you can rate a doctor by click the link in "Add rating".
6. See all the departments, diseases and symptoms information: First you will see all the departments information, then click the department number you will see the diseases belonging to that department. Finally click the diseases' id to see the symptoms.
7. See all the doctors and patients: You will know all the patients and doctors' name and id information.
8. Find disease by symptoms: Click the link in "Symptoms" to see all the symptoms, and then find the disease having that certain symptom.
9. See all the cure information: List all the cure information. You can find a certain doctor's cure records.

