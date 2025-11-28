flow of the step 

- we display all the question in the stepper @Hbstepper

- one step contain 
 <Hbslider> 
 //this is what we want 
 <slide1>
 <originalquestion> <- we want to create this (in originalquestion we want to display Answerinput, the header of Hbstepper )
 </slide1>
 <slide2>
 <Refinementquestion> <- we want to create this  as well (in Refinementquestion we dont want to display Answerinput and the header of Hbstepper )
 </slide2>
 
 
 <Hbsider>
 -Rules
 -when we submit the  answer to the original question we want this animation (its already implemented) show Hboverlayloading , we we get the data
 GO TO -> slide2

 - when we submit the  answer to the Refinement question we want this animation  show Hboverlayloading , we we get the data
 GO TO -> slide1 and put the result in Answerinput

 -To do 
 -for the slider add animation from vue/motion for slide left and right 


Another rule for slider

- when answer to originalquestion is not submitted -> slide shoud contain only 1 element and we dont want to display the DOTS 
- when answer to originalquestion is  submitted -> slide shoud contain 2 elements and we  want to display the DOTS (2 dots)   
/////
"I have no experience"
STATE: INITIAL 
< slider (build in slider)> 
 //this is what we want 
 <slide1>
 <originalquestion> when we click on "I have no experience" we dont want to display the modal anymore but enter another state called "NO EXperince(to create)"
 </slide1>
 < slider (build in slider)> 
 STATE: NO EXPERINCE (similar to state Feeback) 
 < slider (build in slider)> 
 //this is what we want 
 <slide1>
 <originalquestion> 
 </slide1>
 <slide2>
 <No Experince> -> Componenet we have to create 
 </slide2>
 < slider (build in slider)> 