void GetRecord() {           //type out should be an enum that can be ohms, mb or delm units.          
 //prints a string of the form "Module ID, Time, Ohms0,Ohms1, Ohms2, Ohms3, OhmsRef, BatVolts\n"
 //Bat volts is X.n; Delm4 is ref resistor
 char wkStr1[200], wkStr2[100];   //probably more elegant way?
 float tempC= -10.0;
 //probable max of wkStr1 = 136??
// int i=0;
 

 
 wkStr1[0]=0x00;        //initialize to null string.
 strcpy(wkStr1, StationInfo.IDString);   //init wkString with comma
 strcat(wkStr1, ", ");
 //RTCC_TimeGet(&timeinfo);            //set and make sure it is set--confidence, confidence
 //strftime(wkStr2, sizeof(wkStr2), "%x %X", &timeinfo);      //time string in wkStr2
 //strcat(wkStr2, ",");
// if (typeout ==Delm) strcat(wkStr2, "Delm = ");
// if (typeout ==Ohms) strcat(wkStr2, "Ohms = ");
// if (typeout ==Mbars) strcat(wkStr2, "Mbars = ");
//strcat(wkStr1,wkStr2); //now have in wkstr1 name and a comma
         //[4] is ref resistor
//printf("%s\n", wkStr1);       
sprintf(wkStr2, "%04.1f, %04.1f, %04.1f, %04.1f,  %04.1f, ",((double)( SnsrData[0].Delm))/10,\
         ((double)( SnsrData[1].Delm))/10, ((double)( SnsrData[2].Delm))/10,((double)( SnsrData[3].Delm))/10,\
         ((double)( SnsrData[4].Delm))/10);  //inelegant way
strcat(wkStr1,wkStr2);      //tack on the Delm data
//printf("...Delm... %s ****", wkStr1); 
//DELAY_MS(1000);
 
sprintf(wkStr2, "%ld, %ld, %ld, %ld, %ld,", SnsrData[0].BlkOhms, SnsrData[1].BlkOhms, \
         SnsrData[2].BlkOhms, SnsrData[3].BlkOhms, SnsrData[4].BlkOhms);
strcat(wkStr1,wkStr2);      //tack on the Ohms data
//printf("...Ohms... %s*****", wkStr1); 
//DELAY_MS(1000);
     
sprintf(wkStr2, " %d, %d, %d, %d, %d,", SnsrData[0].Mbars, SnsrData[1].Mbars,  \
          SnsrData[2].Mbars, SnsrData[3].Mbars, SnsrData[4].Mbars);   
strcat(wkStr1,wkStr2);      //tack on the Mbars data  
//printf("...Mbars... %s***n", wkStr1);  
//DELAY_MS(1000);
 
sprintf(wkStr2," %.2f,", rdVin() ); 
strcat(wkStr1,wkStr2);      //tack on the Voltage
tempC = rd_temp();

//printf ("//Temp C = %.2fC \n", (double)tempC);
if (tempC> -10.0){       //rd-temp returns -55C if no sensor
    sprintf(wkStr2," %.2f", (double)tempC ); 
}
else strcpy (wkStr2,", ");
strcat(wkStr1,wkStr2);      //tack on the Temp

//SoundBuzz(SOUNDT,100);
//DELAY_MS(100);
//SoundBuzz(SOUNDT,100);
//printf ("\nLength of wkStr1 = %d\n", strlen(wkStr1));
printf("%s\n", wkStr1);    
 NOP;//hopefully
 
 //   printf("Time: %s\n\n",InString);
}
