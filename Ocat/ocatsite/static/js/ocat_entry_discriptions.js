/*
* ocat_entry_discriptions.js
*
* popup window for the Ocat Data Page parameter descriptions
*       Author: t. isobe (tisobe@cfa.harvard.edu)
*       Last Update: Jun. 12, 2015
*   
*/

var seq_nbr = '<font color=blue><b>Sequence Number</b></font><br />'
		+ '<font color=#008080>seq_nbr (target)</font><br />'
		+ 'Sequence # of the particular observation'
	    + '<p>This is a bookkeeping value and rarely changed.</p>';

var status  = '<font color=blue><b>Status</b></font><br />'
		+ '<font color=#008080>status (target)</font><br />'
		+ ' Status of observation'
        + '<p>This is a bookkeeping value and rarely changed.</p>';

var obsid   = '<font color=blue><b>ObsID#</b></font></br>'
		 + '<font color=#008080>obsid (target)</font><br />'
		 + 'ID # used in ObsCat database and on-board Chandra'
		 + '<p>A one to one map with individual observations.</p>';

var proposal_number = '<font color=blue><b>Proposal Number</b></font><br />'
		 + '<font color=#008080>prop_num (prop_info)</font><br />'
		 + 'Proposal Number.'
         + '<p> The proposal from which this and related observations stemmed.</p>';

var proposal_title = '<font color=blue><b>Proposal Title</b></font><br />'
		 + '<font color=#008080>title (prop_info)</font>'
		 + '<p>Title of proposal</p>';

var group_id = '<font color=blue><b>Group ID</b></font><br />' 
		 + '<font color=#008080>group_id (target)</font><br />'
		 + 'Group ID of the observation'
		 + '<p>Bookkeeping tool only used for linked observations.</p>';

var obs_ao_str = '<font color=blue><b>Obs AO Status</b></font><br />'
		 + '<font color=#008080>obs_ao_str (target)</font><br />'
		 + 'AO status of the observation.'
         + '<p> What AO the observation is assigned to.</p>';

var targname = '<font color=blue><b>Target Name</b></font><br />'
		 + '<font color=#008080>targname (target)</font><br />'
		 + '<p>Normal name for the target. Taken from prposal.</p>';

var si_mode = '<font color=blue><b>SI Mode</b></font><br />'
		 + '<font color=#008080>si_mode (target)</font><br />'
		 + '<p>This code is used by the CXC in command generation '
		 + 'to select the appropriate instrument configuration '
		 + 'commands from the controlled Operations Data Base in '
		 + 'order to configure the observation as is specified.'
		 + 'Observers do not use this parameter.</p>';

var aca_mode = '<font color=blue><b>ACA Mode</b></font><br />'
		 + '<font color=#008080>aca_mode (target)</font><br />'
		 + '<p>This code is used by the CXC in command generation '
		 + 'to select the appropriate instrument configuration '
		 + 'commands from the controlled Operations Data Base in '
		 + 'order to configure the observation as is specified.'
		 + 'Observers do not use this parameter.</p>';

var instrument = '<font color=blue><b>Instrument</b></font><br />'
		 + '<font color=#008080>instrument (target)</font><br />'
         + '<p>'
		 + 'Specifies which detector will be on the optical axis during the observation.'
		 + '<font color=red> If an instruement change (ACIS<--->HRC) is required, CDO approval is needed</font>'
         + '</p>'
		 + '<font color=green> Value Range: ACIS-S, ACIS-I, HRC-S HRC-I</font><br />';
		
var grating = '<font color=blue><b>Grating</b></font><br />'
		 + ' <font color=#008080>grating (target)</font><br />'
		 + '<p>Specifies which grating to use. The default is NONE which specifies no grating (direct imaging). '
		 + '<font color=red>All changes require CDO approval. '
		 + 'Adding a grating requires count rate, and 1st Order Rate</font>.</p>'
		 + '<font color=green> Value Range: NONE, HETG, LETG</font>';
		
var otype = '<font color=blue><b>Type</b></font><br />'
		 + '<font color=#008080>type (target)</font><br />'
		 + '<p>Type of Observation.</p>'
	 	 + '<font color=green>Value Range: GO, TOO, GTO, CAL, DDT, CAL_ER, ARCHIVE, CDFS</font>';

var pi_name = '<font color=blue><b>PI Name</b></font><br />'
		 + '<font color=#008080>person_short (prop_info)</font><br />'
		 + '<p>Last name of Principal Investigator</p>';

var observer = '<font color=blue><b>Observer</b></font><br />'
		  + '<font color=#008080>coi_contact (prop_info)</font><br />'
		  + '<p>Last name of Observer if it is different from that of PI '
	      + 'It is the OBSERVER, not the PI who is responsible for the observtion setup.</p>';

var approved_exposure_time = '<font color=blue><b>Exposure Time</b></font><br />'
		 + '<font color=#008080>approved_exposure_time (target)</font><br />'
		 + '<p>Exposure time for the Obsid. If your total time is higher than this, ';
		 + 'it may have been split due to orbital constraints. <font color=red>If the User wants to '
		 + 'to split the observation, this must be done through a separate CDO request</font>.</p>';

var rem_exp_time ='<font color=blue><b>Remaining Exposure Time</b></font><br />'
		 + '<font color=#008080>rem_exp_time (target)</font><br />'
		 + '<p>The remaining time which still must be scheduled on this '
		 + 'target to give the observer the approved_exposure. ' 
		 + 'It is computed dynamically based on the mission planning and '
		 + 'data analysis processes.</p>'
         + '<p>If it is less than 20% of the approved time, additional obserations '
		 + 'will not be performed.</p>';

var joint = '<font color=blue><b>Joint Proposal</b></font><br />'
		 + '<font color=#008080>joint (prop_info)</font><br />'
	   	 + '<p>A flag for whether this observation is coordinated with another observatory. '
		 + 'This is only for proposed and approved coordination. For post facto '
		 + 'coordination, use the "Coordinated" '
		 + 'field in the "Other Constraints" section or the "REMARLS" area.</p>';

var prop_hst = '<font color=blue><b>HST Approved Time</b></font><br />'
		 + '<font color=#008080>hst_approved_time (prop_info)</font><br />'
		 + '<p>TAC approved HST time.</p>';

var prop_noao = '<font color=blue><b>NOAO Approved Time</b></font><br />'
		 + '<font color=#008080>noao_approved_time (prop_info)</font><br />'
		 + '<p>TAC approved NOAO time.</p>';

var prop_xmm = 'XMM Approved Time</b></font><br />'
		 + '<font color=#008080>xmm_approved_time (prop_info)</font><br />'
		 + '<p>TAC approved XMM time.</p>';

var prop_rxte = '<font color=blue><b>RXTE Approved Time</b></font><br />'
		 + '<font color=#008080>rxte_approved_time (prop_info)</font><br />'
		 + '<p>TAC approved RXTE time.</p>';

var prop_vla = '<font color=blue><b>VLA Approved Time</b></font><br />'
		 + '<font color=#008080>vla_approved_time (prop_info)</font><br />'
		 + '<p>TAC approved VLA time.</p>';

var prop_vlba = '<font color=blue><b> VLBA Approved Time</b></font><br />'
		 + '<font color=#008080>vlba_approved_time (prop_info)</font><br />'
		 + '<p>TAC approved VLBA time.</p>';

var soe_st_sched_date = '<font color=blue><b>Schedule Date</b></font><br />'
		 + '<font color=#008080>soe_st_sched_date (target)</font><br />'
		 + '<p>Observation schedule date</p>'
		 + '<p>This is the date the observation will take place. '
		 + 'This date is not known until the detailed scheduling has begun. '
		 + 'Usually less than 10 days before the observation.</p> '
		 + '<p>Once this date is konwn it is virtually impossible to change '
		 + 'any setting. <span style="color:red">CXC director and CXO flight '
         + 'director approval would be needed.</span> </p>';

var lts_lt_plan  = '<font color=blue><b>LTS Date</b></font><br />'
		 + '<font color=#008080>lts_lt_plan (target)</font><br />'
		 + 'LTS planed date'
		 + '<p>Week of the observation for planning purposes.  This date '
		 + 'may change, especially if the target is considered a pool target. '
		 + 'Typically, 15 observations are moved each week.</p> '
		 + '<p>See the bottom of the long term schedule for recent changes.</p>';

var ra = '<font color=blue><b>RA(HMS)</b></font><br />'
		 + '<font color=#008080>ra (target)</font><br />'
		 + '<p>The Right Ascension of the source in mandatory J2000 coordinate system.</p>'
		 + '<p>The standard format is HH MM SS.S - hours, minutes, seconds, '
		 + 'separated by spaces. For usint reading, a decimal degree format is required.</p> '
         + '<p><font color=red>If RA + DEC change is larger than 8 arc minutes, CDO '
         + 'approval is required and cannot be made from this interface.</font>.</p>';
		
var dec = '<font color=blue><b>DEC(HMS)</b></font><br />'
		 + '<font color=#008080>dec (target)</font><br />'
		 + '<p>The declination of the source in mandatory J2000 coordinate system.</p>'
		 + '<p>The standard format is +/-DD MM SS.S - sign, degrees,arcminutes, '
		 + 'arcseconds, separated by spaces For usint reading, decimal degree format is required.</p>'
         + '<p><font color=red>If RA + DEC change is larger than 8 arc minutes, CDO '
         + 'approval is required and cannot be made from this interface.</font></p>';

var planned_roll = '<font color=blue><b>Planned Roll</b></font><br />'
		 + '<font color=#008080>N/A</font><br />'
	 	 + '<p>This is the MP planned roll. This is not an editable field.</p> '
		 + '<p>See http://hea-www.harvard.edu/asclocal/mp/lts/lts-current.html.</p>';

var roll_obsr = '<font color=blue><b>Roll Observed</b></font><br />'
		 + '<font color=#008080>soe_roll (soe)</font><br />'
	 	 + '<p>This is the observed roll. This is not an editable field. </p>'
		 + '<p>See Roll Constraints if you need to constrain the roll.</p>';

var dra='<font color=blue><b>RA</b></font><br />'
		 + 'RA in degrees. This is the RA in decimal coordinates.<br />';
		 + '<p>This is the system used by the mission planners. The spacecraft '
		 + 'will point here. The MHS version is soloely for convenience. </p>'
		 + '<p><font color=red>If RA + DEC change is rather than 8 arc minutes, '
		 + 'CDO approval is required.</font></p>';

var ddec = '<font color=blue><b>DEC</b></font><br />'
		 + '<p>DEC in degrees. This is the DEC in decimal coordinates.</p>'
		 + '<p>This is the system used by the mission planners. The spacecraft '
		 + 'will point here. The MHS version is soloely for convenience.</p>'
		 + '<p><font color=red>If RA + DEC change is rather than 8 arc minutes, '
		 + 'CDO approval is required.</font></p>';

var y_det_offset = '<font color=blue><b>Offset Y</b></font><br />'
		 + '<font color=#008080>y_det_offset (target)</font><br />'
		 + '<p>This motion moves the target position away from the aimpoint '
		 + '(and thus away from the best focus position) by yawing the spacecraft '
		 + 'away from the target. Sense: negative Y offset moves the target '
		 + 'aways from the aimpoint in the direction of S4 on ACIS-S '
		 + '(ie further onto the S3 chip). Refer to Figure 6.1 in the Proposers Guide '
		 + 'Recommendations: ACIS-S imagin observations Y-offset -0.33 arcmins.</p> '
		 + '<p><font color=green> Value Range: -120.0 to +120.0</font>.</p>';

var z_det_offset = '<font color=blue><b>Offset Z</b></font><br />'
		 + '<font color=#008080>z_det_offset (target)</font><br />'
		 + '<p>This motion moves the target position away from the aimpoint '
		 + '(and thus away from the best focus position) by pitching the spacecraft '
		 + 'away from the target. Sense: positive offset moves the traget '
		 + 'towards the readouts in ACIS-S (ie away form ACIS-I). Refer to Figure 6.1 '
		 + 'in the Proposers Guide. Value is angle in arcmin measured from the aimpoint.</p>'
		 + '<p><font color=green> Value Range: -120.0 to +120.0</font><br />';
		
var trans_offset = '<font color=blue><b>Z-Sim</b></font><br />'
		 + '<font color=#008080>trans_offset (sim)</font><br />'
         + '<p>This is a motion of the SIM and thus the aimpoint away from '
         + 'the default position on the detector along the z-axis '
         + '(the SIM Translation direction. '
         + 'Sense: a negative motion moves the aimpoint (and the '
		 + 'target) towards the readouts on ACIS-S (ie. away from ACIS-I).</p>'
         + '<p>Units: mm (scale: 2.93mm/arcmin)</p>'
 		 + '<p><b>Recommendations</b></p>'
		 + '<table border=1 cell-padding=2>'
 		 + '<tr><th>Configuration</th><th>Mode</th><th>SIM z (mm)</th></tr>'
 		 + '<tr><th> HETG+ACIS-S </th><td> TE </td><td> -3 </td></tr>'
 		 + '<tr><th> HETG+ACIS-S </th><td> CC </td><td> -4 </td></tr>'
 		 + '<tr><th> LETG+ACIS-S </th><td> TE </td><td> -8 </td></tr>'
 		 + '<tr><th> LETG+ACIS-S </th><td> CC </td><td> -8 </td></tr>'
		 + '</table>'
		 + '<p><font color=green> Value Range: NULL, -190.5 to 126.621.</font><br /></p>';
		
var focus_offset = '<font color=blue><b>Sim-Focus</b></font><br />'
		 + '<font color=#008080>focus_offset (sim)</font><br />'
		 + '<p>Focus offset on the SIM, in mm.</p>';
		
var defocus = '<font color=blue><b>Focus</b></font><br />'
		 + '<font color=#008080>defocus (target)</font><br />'
		 + '<p>A number determining how far in mm the focal plane will '
		 + 'be moved toward or away from the mirrors.</p>';

var raster_scan = '<font color=blue><b>Raster Scan</b></font><br />'
		 + '<font color=#008080>raster_scan (target)</font><br />'
		 + '<p>A flag indicating whether the observation will be a raster scan.</p>'
		 + '<p><font color=green>Value Ranges: NULL, Y, N </font></p>';
		
var dither_flag = '<font color=blue><b>Dither</b></font><br />'
		 + '<font color=#008080>dither_flag (target)</font><br />'
		 + '<p>A flag indicating whether a dither is required for the observation. '
		 + 'The default "NULL" means dither is preset to the standard dither '
		 + 'pattern. <b>It does not mean no dither.</b></p>'
         + '<p>"Y" means that you are using your own dither parameters, these may be '
		 + 'rejected on final review, so contact CDO ahead of time for review.</p>'
         + '<p>"N"means no dither again this may be rejected by the SI team during final '
         + 'review so contact CDO to avoid surprises.</p>'
		 + '<p>The dither parameters must not violate the requirement on peak dither rate:</p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
 		 + '<p>This peak dither rate can be used to evaluate the effect of image '
		 + 'blurring during an ACIS frame integration.</p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table> '
		 + '<p><font color=green> Value Range: Y, N, NULL</font></p>';

var y_amp  = '<font color=blue><b>Y Amplitude</b></font><br />'
		 + '<font color=#008080>y_amp (dither)</font><br />'
		 + '<p>Dither Y amplitude in arcsec.'
		 + 'The value is also displayed in degree.</p>'
         + '<p>The dither parameters must not violate the requirement'
         + 'on peak dither rate:p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
         + '<p>This peak dither rate can be used to evaluate the effect of '
         + 'image blurring during an ACIS frame integration.</p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table> ';


var y_freq  = '<font color=blue><b>Y Frequency</b></font><br />'
		 + '<font color=#008080>y_freq (dither)</font><br />'
		 + '<p>Dither Y frequency in arcsec/sec. '
         + 'The value is also displayed in degree/sec.</p>'
         + '<p>The dither parameters must not violate the requirement '
         + 'on peak dither rate:</p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
         + '<p>This peak dither rate can be used to evaluate the effect of'
         + 'image blurring during an ACIS frame integration.</p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table>';

		
var y_phase = '<font color=blue><b>Y Phase</b></font><br />'
		 + '<font color=#008080>y_phase (dither)</font><br />'
		 + '<p>Dither Y phase in degrees.</p> '
         + '<p>The dither parameters must not violate the requirement'
         + 'on peak dither rate:</p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
         + '<p>This peak dither rate can be used to evaluate the effect of '
         + 'image blurring during an ACIS frame integration.</p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table>';

		
var z_amp = '<font color=blue><b>Z Amplitude</b></font><br />'
		 + '<font color=#008080>z_amp (dither)</font><br />'
		 + '<p>Dither Z amplitude in arcsec. '
		 + 'The value is also displayed in degree.'
         + '<p>The dither parameters must not violate the requirement'
         + 'on peak dither rate:</p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
         + '<p>This peak dither rate can be used to evaluate the effect of '
         + 'image blurring during an ACIS frame integration. </p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table> ';

		
var z_freq = '<font color=blue><b>Z Frequency</b></font><br />'
		 + '<font color=#008080>z_freq (dither)</font><br />'
		 + '<p>Dither Z frequency in arcsec/sec</p>'
         + '<p>The dither parameters must not violate the requirement '
         + 'on peak dither rate:</p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
         + '<p>This peak dither rate can be used to evaluate the effect of '
         + 'image blurring during an ACIS frame integration.</p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table> ';

		
var z_phase = '<font color=blue><b>Z Phase</b></font><br />'
		 + '<font color=#008080>z_phase (dither)</font><br />'
		 + '<p>Dither Z phase in degrees</p>'
         + '<p>The dither parameters must not violate the requirement '
         + 'on peak dither rate:</p>'
 		 + '<p><b><em> '
         + '[(2&pi;&sdot; y_amp / y_period)<sup>2</sup> + (2&pi;&sdot; z_amp / z_period)<sup>2</sup>]<sup>1/2</sup> '
         + '&lt; 0.22 (arcsec/sec)'
         + '</em></b></p>'
         + '<p>This peak dither rate can be used to evaluate the effect of '
         + 'image blurring during an ACIS frame integration.</p>'
		 + '<table border= 1>'
		 + '<tr><th>Parameter</th>    <th> ACIS Default</th>                <th> HRC Default</th></tr>'
		 + '<tr><th>y_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" =0.0056 deg</td></tr>'
		 + '<tr><th>y_frequency</th>  <td>1296"/sec<br />=0.36 deg/sec</td> <td>1191"/sec<br />=0.331 deg/sec</td></tr>'
		 + '<tr><th>y_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '<tr><th>z_amp</th>        <td>8" = 0.002222 deg</td>            <td>20" = 0.0056 deg</td></tr>'
		 + '<tr><th>z_frequency</th>  <td>1832"/sec<br />=0.509 deg/sec</td><td>1648"/sec<br />= 0.468 deg/sec</td></tr>'
		 + '<tr><th>z_phase</th>      <td>0</td>                            <td>&#160</td></tr>'
		 + '</table> ';

		
var uninterrupt = '<font color=blue><b>Uninterrupted Obs</b></font><br />'
		 + '<font color=#008080>uninterrupt (target)</font><br />'
		 + '<p>A flag for whether the observation can be interrupted. '
		 + '<font color=red>CDO approval required to change this to Y or P</font>. '
		 + '<p>This indicates a preference this will be noted by '
		 + 'mission planning, but is not included by V&V when '
		 + 'evaluating the success for the observation.<p>'
		 + '<p><font color=green> Value Range: Y, P, N, NULL</font></p>';

var extended_src = '<font color=blue><b>Extended SRC</b></font><br />'
		 + '<p>RPS form from the proposal submission.</p>'
		 + '<p><font color=green> Value Range: Y,  N</font></p>';
		
var obj_flag = '<font color=blue><b>Solar System Object</b></font><br />'
		 + '<font color=#008080>obj_flag (target)</font><br />'
		 + '<p>A flag for a solar system observation.</p>'
		 + '<p>This field is used to allow the ground system to automatically '
		 + 'calculate the position of the ss object or moving target for you. '
		 + 'It has not been used in flight. We recommend working with CDO to '
		 + 'calculate the exact position.</p>'
		 + '<p><font color=green> Value Range: NO, MT, or SS</font></p>';
		
var object = '<font color=blue><b>Object</b></font><br />'
		 + '<font color=#008080>object (target)</font><br />'
		 + '<p>Solar system objects.</p>'
		 + '<p>If you are so bold as to let the ground system calculate the '
		 + 'pointing for you, this is where you input the object name.</p> '
		 + '<p><font color=green> Value Range:  NONE, NEW, COMET, EARTH, JUPITER,'
		 + 'MARS, MOON, NEPTUNE, PLUTO, SATURN, URANUS, or VENUS</font></p>';
		
var photometry_flag = '<font color=blue><b>Photometry</b></font><br />'
		 + '<font color=#008080>photometry_flag (target)</font><br />'
		 + '<p>A flag for photometry which indicates whether observer '
		 + 'will use one of the 5 star tracking slots for traget '
		 + 'photometry. See the POG section Section 5.9.3.1 for details.</p>'
		 + '<p><font color=green> Value Range: NULL, Y, N</font></p>';
		
var vmagnitude = '<font color=blue><b>V Mag</b></font><br />'
		 + '<font color=#008080>vmagnitude (target)</font><br />'
		 + '<p>V Magnitude of the target if optical monitor data is selected.</p>'
		 + '<p><font color=green> Value Range: NULL, -15 to 20.</font></p>';
		
var est_cnt_rate = '<font color=blue><b>Count Rate</b></font><br />'
		 + '<font color=#008080>est_cnt_rate (target)</font><br />'
		 + '<p>Estimated count rate for the observation counts/sec. '
		 + 'A value is required, if a grating is requested.</p>'
		 + '<p><font color=green> Value Range: NULL, 0 to 100,000.</font></p>';

var forder_cnt_rate = '<font color=blue><b>1st Order Rate</b></font><br />'
		 + '<font color=#008080>forder_cnt_rate (target)</font><br />'
		 + '<p>First order count rate in counts/sec for ACIS-S+grating '
		 + 'and HRC-S+grating observations. A value is required, if a grating is requested.</p>'
		 + '<p><font color=green> Value Range: NULL, 0 to 100,000.</font></p>';
		
var window_flag = '<font color=blue><b>Window Flag</font><br />'
		 + '<font color=#008080>window_flag (taget)</font><br />'
		 + '<p>This can only be set to "Y" if this is a TAC or CDO ';
		 + 'approved constraint.  Set to "P" if you have a preference '
		 + 'and we will do the best we can to accommodate your entries.</p>'
		 + '<p><font color=green> Value Range: NULL, N, Y, P</font></p>';

var time_ordr = '<font color=blue><b>Rank</b></font><br />'
		 + '<font color=#008080>ordr(timereq)</font><br />'
		 + '<p>You can have multiple time constraints on a given target. '
		 + 'Increase this number to prodcue multiple window. If you change '
		 + 'this value, numbers of input windows for tstart, tstop change accordingly.</p>';

var window_constraint = '<font color=blue><b>Window Constraint</b></font><br />'
		 + '<font color=#008080>window_constraint (timereq)</font><br />'
		 + '<p>A flag indicating whether a time window is required for the observation. '
		 + '<font color=red>"Y" is only allowed if TAC or CDO approved</font>.</p>'
		 + '<p><font color=green> Value Range:  NULL, N, Y, P</font></p>';

var tstart = '<font color=blue><b>Start</b></font><br />'
		 + '<font color=#008080>tstart (timereq) </font><br />'
		 + '<p>Date and time to start time critical observation. Time must '
		 + 'be 24 hr system in hh:mm:ss format.'
		 + '<I> Time is in UT</I>.</p>';
		
var tstop = '<font color=blue><b>Stop</b></font><br />'
		 + '<font color=#008080>tstop (timereq) </font><br />'
		 + '<p>Date and time to start time critical observation. '
		 + 'Time must be 24 hr system in hh:mm:ss format. '
		 + '<I> Time is in UT</I></p>';
		
var roll_flag = '<font color=blue><b>Roll Flag</b></font><br />'
		 + '<font color=#008080>roll_flag (taget)</font><br />'
		 + '<p>This can only be set to "Y" if this is a TAC or CDO approved constraint. '
		 + 'Set to "P" if you have a preference and we will do the best we can to '
		 + 'accommodate your entries</p>'
		 + '<p><font color=green> Value Range: NULL, N, Y, P</font></p>';

var roll_ordr = '<font color=blue><b>Rank</b></font><br />'
		 + '<font color=#008080>ordr (rollreq)</font><br />'
		 + '<p>Order for the roll constraint. If you change this value, '
		 + 'numbers of roll constraint, roll180, roll, and roll tolerance change accordingly. </p>';

var roll_constraint = '<font color=blue><b>Roll Constraint</b></font><br />'
		 + '<font color=#008080>roll_constraint (rollreq)</font><br />'
		 + '<p>A flag indicating whether a roll constraint is required for the observation. '
		 + 'This can only be set to "Y" if this is a TAC or CDO approved constraint. '
		 + 'Set to "P" if you have a preference and we will do the best we can to '
		 + 'accommodate your entries.</p>'
		 + '<p><font color=green> Value Range: NULL, N, Y, P</font></p>';
		
var roll_180 = 'Roll180?</b></font><br />'
		 + '<font color=#008080>roll_180(rollreq)</font><br />'
		 + '<p>A flag indicating whether 180 degree flip in the roll is acceptable for the observation.</p>'
		 + '<p><font color=green> Value Range:  NULL, N,  Y</font></p>';
		
var roll = '<font color=blue><b>Roll</b></font><br />'
		 + '<font color=#008080>roll(rollreq)</font><br />'
		 + '<p>The spacecraft roll angle is the angle between celestial north '
		 + 'and the spacecraft +Z axis projected on the sky.  Measured in degrees.</p>'
		 + '<p><font color=green> Value Range: NULL, 0 to 360.</font></p>';
		
var roll_tolerance = '<font color=blue><b>Roll Angle Tolerance</b></font><br />'
		 + '<font color=#008080>roll_tolerance (rollreq)</font><br />'
		 + '<p>Tolerance on the Roll Angle.</p>'
		 + '<p><font color=green> Value Range: NULL,0 to 360</font></p>';
		
var constr_in_remarks = '<font color=blue><b>Constraints in Remarks?</b></font><br />'
		 + '<font color=#008080>constr_in_remarks (target)</font><br />'
         + '<p>A flag indicating whether there is a description '
         + 'of any constraints in a remark section.</p>'
         + '<p>Note that the Constraint in Remarks section '
         + '<i> cannot be used to add in '
		 + 'constraints that were not approved through peer review,</i> but rather '
		 + 'to explain existing constraints and preferences.</p>'
		 + '<p><font color=green> Value Range: NULL, Y, P,  N </font></p>';
		
var phase_constraint_flag = '<font color=blue><b>Phase Constraint</b></font><br />'
		 + '<font color=#008080>phase_constraint_flag (target)</font><br />'
		 + '<p>A flag indicating whether the observation is targeted at a particular '
		 + 'orbital phase. If so, additional data is required.</p>'
         + '<p> If this is set for Y '
		 + 'or P, values for the Epoch of phase 0 , the Period of the phenomena, '
		 + 'Phase Start, Phase Start Margin, Phase Min, Phase Min Margin are required.</p>'
		 + '<p><font color=green> Value Range: NULL, N, Y, P</font></p>';
			
var phase_epoch = '<font color=blue><b>Phase Epoch</b></font><br />'
		 + '<font color=#008080>phase_epoch (phasereq)</font><br />'
		 + '<p>For Phase Dependent observations, this is the reference date (MJD). '
		 + 'The observations will be made at an integral number of Periods from this date.</p> '
		 + '<p><font color=green>Value Ranges: > 46066.0</font></p>';
		
var phase_period = '<font color=blue><b>Phase Period</b></font><br />'
		 + '<font color=#008080>phase_period (phasereq)</font><br />'
		 + '<p>Period in days between phase dependent observations.</p>';

var phase_start =  '<font color=blue><b>Phase Start</b></font><br />'
		 + '<font color=#008080>phase_start (phasereq)</font><br />'
		 + '<p>The earliest phase for the observation.</p> '
		 + '<p><font color=green>Value Ranges:  0 to 1</font></p>';
		
var phase_start_margin = '<font color=blue><b>Phase Start Margin</b></font><br />'
		 + '<font color=#008080>phase_start_margin (phasereq)</font><br />'
	 	 + '<p>The allowable error for mission planning on the previous entry.</p> '
		 + '<p>Remeber to include the observation duration when thinking about this.</p> '
		 + '<p><font color=green>Value Ranges: 0 to 0.5</font></p>';
		
var phase_end = '<font color=blue><b>Phase End</b></font><br />'
		 + '<font color=#008080>phase_end (phasereq)</font><br />'
		 + '<p>Maximum orbital phase to be observed.  </p>'
		 + '<p><font color=green>Value Ranges:  0 to 1</font></p>';
		
var phase_end_margin = '<font color=blue><b>Phase End Margin</b></font><br />'
		 + '<font color=#008080>phase_end_margin (phasereq)</font><br />'
		 + '<p>Error on the maximum orbital phase. Include the observation '
		 + 'duration when thinking about this value.</p>'
		 + '<p><font color=green>Value Ranges: 0 to 0.5</font></p>';

var monitor_flag = '<font color=blue><b>Monitoring Observation</b></font><br />'
        + '<p>The following 3 fields are used for monitoring '
        + 'observations.  While the full pattern of observations '
        + 'can be complicated, here you concern yourself with a '
        + 'previous observation in the group and the time (in '
        + 'days) between that observation and this one.</p> '
        + '<p>The start time for a monitoring observation is '
        + 'determined by the time the previous observation ENDED, '
        + 'and only has to BEGIN between Min Int and Max Int, '
        + 'it does not need to fall fully within these boundaries.</p> '
        + '<p><b>Notes:</B> It is possible to have monitoring '
        + 'observations where '
        + 'each obsid is linked to the first in the series '
        + '(ie. you want to space them from the initial obsid by '
        + 'some number of days and do not want that to be impacted '
        + 'by the tolerance on the previous one).  In this case, '
        + 'Follows ObsID# should be the first in the sequence.</p> '
        + '<p>It is also possible for the first observation in a '
        + 'monitoring series to be time constrained or otherwise '
        + 'constrained as specified by the observer, though it '
        + 'does not become a time constrained observation simply '
        + 'because it is the 1st observation in a monitoring series.</p> '
		+ '<p><b>If group_id has a value, monitoring observation '
		+ 'must be null.</p>';
		
var pre_id = '<font color=blue><b>Follows ObsID#</b></font><br />'
		 + '<font color=#008080>pre_id (target)</font><br />'
		 + '<p>Gives the ObsId # in which this observation follows. There cannot be any time constraints.</p>';

var pre_min_lead = '<font color=blue><b>Min Int</b></font><br />'
		 + '<font color=#008080>pre_min_lead (target)</font><br />'
		 + '<p>Monitoring Observation: The minimum interval between monitoring observations.  Units are days</p>'
		 + '<p><font color=green>Value Ranges: NULL, 0 to 364</font></p>';
		
var pre_max_lead = '<font color=blue><b>Max Int</b></font><br />'
		 + '<font color=#008080>pre_max_lead (target)</font><br />'
		 + '<p>Monitoring Observation: The maximum interval between monitoring observations.  Units are days.</p>'
		 + '<p><font color=green>Value Ranges: NULL, 0.01 to 365</font></p>';
		
var multitelescope = '<font color=blue><b>Coordinated Observation</b></font><br />'
		 + '<font color=#008080>multitelescope (target)</font><br />'
		 + '<p>A flag indicating whether this is coodinated observation.</p> '
		 + '<p>This differs from a joint proposal in that the telescope time involved comes '
		 + 'from multiple TACs. It CAN be listed as a preference if telescope time has been '
		 + 'obtained after the TAC approval of this observation.</p> '
		 + '<p><font color=red>CDO approval is required to change the value to "Y".</font></p> '
		 + '<p><font color=green>Value Ranges: Y,P, N</font></p>';
		
var observatories = '<font color=blue><b>Observatories</b></font><br />'
		 + '<font color=#008080>observatories (target)</font><br />'
		 + '<p>Names of coordinated observatories.</p> '
		 + '<p><font color=red>CDO approval is required to change the value,</font> '
		 + 'if the "Coordinated Observation" flag is set to "Y"<br />';

var multitelescope_interval = '<font color=blue><b>Max Coordination Offset</b></font><br />'
		 + '<font color=#008080>multitelescope_interval (target)</font><br />'
		 + '<p>The maximum time interval for coordination with ground-based observatories. '
		 + 'The units are days (floating point).</p> '
		 + '<p><font color=red>CDO approval is required to change the value,</font> '
		 + 'if the "Coordinated Observation" flag is set to "Y"</p>';
		 
var hrc_timing_mode = '<font color=blue><b>HRC Timing Mode</b></font><br />'
		 + '<font color=#008080>timing_mode (hrcparam)</font><br />'
		 + '<p>This timing mode consists of using the HRC-S in the imaging mode.';
		 + 'Only the center segment is active. The overall detector background is about 50 cnt/sec.';
		 + 'Sources with rates up to the telemetry limit can be observed  with no lost events.</p> ';
		 + '<p><font color=green>Value Ranges: "Y", "N"</font></p>';

var hrc_zero_block =  '<font color=blue><b>Zero Block</b></font><br />'
		 + '<font color=#008080>zero_block (hrcparam)</font><br />'
		 + '<p>Logical value indicating zero-order blocking. The defalut is "N". '
		 + 'The spectrum zero order may be blocked if desired.</p> '
		 + '<p>Using zero-block moves a shutter-blade vignettes much of the '
		 + 'central plate of the HRC-S or a large portion of the center of the '
		 + 'HRC-I.  The impact on the HRC-S can be seen here.</p>'
		 + '<p><font color=green>Value Ranges: "NULL", "Y", "N"</p>';

var hrc_si_mode = '<font color=blue><b>HRC SI Mode</b></font><br />'
		+ '<font color=#008080>si_mode (hrcparam)</font><br />'
        + '<p>A link to a listing of current and default HRCMODEs is available.</p>'
		+ '<p>If a user wishes to request the use of one of these ofr have a custom '
		+ 'one built the request should be put into the comment area.</p>';
		
var exp_mode = '<font color=blue><b>ACIS Exposure Mode</b></font><br />'
		 + '<font color=#008080>exp_mode (acisparam)</font><br />'
		 + '<p>The exposure mode for ACIS.'
		 + 'See POG section 6.12 for details.</p>'
		 + '<p><font color=green>Value Ranges: TE (Timed Exposure), CC (Continuous Clocking)</font></p>';
		
var bep_pack =  '<font color=blue><b>Event TM Format</b></font><br />'
		 + '<font color=#008080>bep_pack (acisparam)</font><br />'
		 + '<p>Event Telemetry Format: Event Telemetry Format controls the '
		 + 'packing of the data into the telemetry stream. This must be N, if frame_time has a value. '
		 + 'See POG section 6.13.2 for details.</p>'
		 + '<p><font color=green>Value Ranges:  Faint (TE,CC), Very Faint(TE), Faint+Bias(TE), Graded(TE,CC)</font></p>';

var frame_time = '<font color=blue><b>Frame Time</b></font><br />'
		 + '<font color=#008080>frame_time (acisparam)</font><br />'
         + '<p>User specified frame time (in seconds) to use.</p> '
         + '<p>ACIS can accommodate frametimes from 0.1 to 10.0 s, '
         + 'however, frametimes less than 0.4s will introduce a deadtime.  One '
         + 'CCD can be readout with a 128 row subarray in 0.4s with no deadtime. '
         + 'Any faster than that and there will be deadtime.</p> '
		 + '<p>Most Efficient must be N if  frame_time has a value.</p>'
		 + '<p><font color=green>Value Ranges:  NULL, 0 to 10</font></p>';

var most_efficient = '<font color=blue><b>Most Efficient</b></font><br />'
		 + '<font color=#008080>most_efficient (acisparam)</font><br />'
		 + '<p>A flag indicating whether the observation requires the most efficient setting. '
		 + 'This must be N, if frame_time has a value.</p>'
		 + '<p><font color=green>Value Ranges: NULL, Y, N</font></p>';
		
var standard_chips = '<font color=blue><b>Standard Chips</b></font><br />'
		 + '<font color=#008080>standard_chips (acisparam)</font><br />'
		 + '<p>Logical value indicating that the standard ACIS chips should be used. The default in N. '
		 + 'A "Y" answer will activate the 6 standard ACIS chips. If N is '
		 + 'selected, usint needs to select ccd chips from: I0, I1, I2, I3, S0, S1, S2, S3, S4, S5.</p>' 
		 + '<p><font color=green>Value Ranges: NULL, Y, N</font></p>';
		
var fep = '<font color=blue><b>FEP</b></font><br />'
		 + '<font color=#008080>fep (acisparam)</font><br />'
		 + '<p>FEP </p>'
		 + '<p><font color=green>Value Ranges:NULL, I0, I1, I2, I3, S0, S1, S2, S3, S4, S5</font></p>';
		
var dropped_chip_count = '<font color=blue><b>Dropped Chip Count</b></font><br />'
		 + '<font color=#008080>dropped_chip_count(acisparam)</font><br />'
		 + '<p>This tells you # of optional chips dropped. </p>'
		 + '<p><font color=green>Value Ranges:NULL, 0 to 5</font></p>';
		
var ccdi0_on = '<font color=blue><b>I0</b></font><br />'
		 + '<font color=#008080>ccdi0_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip I0 on? </p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccdi1_on = '<font color=blue><b>I1</b></font><br />'
		 + '<font color=#008080>ccdi1_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip I1 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccdi2_on = '<font color=blue><b>I2</b></font><br />'
		 + '<font color=#008080>ccdi2_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip I2 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccdi3_on = '<font color=blue><b>I3</b></font><br />'
		 + '<font color=#008080>ccdi3_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip I3 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccds0_on = '<font color=blue><b>S0</b></font><br />'
		 + '<font color=#008080>ccds0_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip S0 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccds1_on = '<font color=blue><b>S1</b></font><br />'
		 + '<font color=#008080>ccds1_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip S1 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccds2_on = '<font color=blue><b>S2</b></font><br />'
		 + '<font color=#008080>ccds2_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip S2 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccds3_on = '<font color=blue><b>S3</b></font><br />'
		 + '<font color=#008080>ccds3_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip S3 on?< /p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccds4_on = '<font color=blue><b>S4</b></font><br />'
		 + '<font color=#008080>ccds4_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip S4 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var ccds5_on = '<font color=blue><b>S5</b></font><br />'
		 + '<font color=#008080>ccds5_on (acisparam)</font><br />'
		 + '<p>Do you want ACIS chip S5 on?</p>'
		 + '<p>There is a limit of 6 chips on, and options of dropping CCDs if needed '
		 + 'OPT1 will be dropped first, and OPT5 will be the last.</p>'
		 + '<p><font color=green>Value Ranges:Y, O1, O2, O3, O4, O5, N, NULL</font></p>';

var subarray = '<font color=blue><b>Use Subarray</b></font><br />'
		 + '<font color=#008080>subarray (acisparam)</font><br />'
		 + '<p>A subarray is a reduced region of the CCDs (all of the CCDs that '
		 + 'are turned on) that will be read.  A reduced region may also help '
	 	 + 'to reduce the effects of pulse pile-up.  The first box indicates '
		 + 'whether  the proposer intends to use the subarray capability.'
		 + '  The default is "NO".</p>'
		 + '<p>If "YES" is selected, the Start, Rows must be filled. '
		 + 'The old default subarrays are:</p>'
		 + '<table cellpadding=2><tr>'
		 + '<th>subarray:</th><th colspan=2>1/8</th><th colspan=2>1/4</th><th colspan=2>1/2</th>'
		 + '</tr><tr>'
		 + '<th>aimpoint:</th><td>start</td><td>rows</td><td>start</td><td>rows</td><td>start</td><td>rows</td>'
		 + '</tr><tr>'
		 + '<th>ACIS-I  :</th><td>897</td><td>128</td><td>768</td><td>256</td><td>513</td><td>512</td>'
		 + '</tr><tr>'
		 + '<th>ACIS-S  :</th><td>449</td><td>128</td><td>385</td><td>256</td><td>257</td><td>512</td>'
		 + '</tr></table>'
		 + '<p><font color=green>Value Ranges: N (NO) and CUSTOM (YES)</font></p>';

var subarray_start_row = '<font color=blue><b>Start</b></font><br />'
		 + '<font color=#008080>subarray_start_row (acisparam)</font><br />'
		 + '<p>Subarray: The starting row that will be read for processing custom subarrays. '
		 + 'If it is not NULL, Use Subarray must be YES, and Rows must be filled. '
		 + 'See section 6.2.13 of the POG</p>'
		 + '<p><font color=green>Value Ranges: NULL, 1 to 925 </font></p>';
		
var subarray_row_count = '<font color=blue><b>Rows</b></font><br />'
		 + '<font color=#008080>subarray_row_count (acisparam)</font><br />'
		 + '<p>Subarray: The number of rows that will be read for processing '
		 + 'custom subarrays.  If it is not NULL, Use Subarray must be YES, and Start must be filled. '
		 + 'See section 6.2.13 of the POG for details</p>'
		 + '<p><font color=green>Value Ranges: NULL, 100 to 1024 </font></p>' ;

var subarray_frame_time = '<font color=blue><b>Frame Time</b></font><br />'
		 + '<font color=#008080>subarray_frame_time (acisparam)</font><br />'
		 + '<p>Subarray - Frame Time: The Frame Time is the fundamental '
		 + 'unit of exposure for ACIS. The higher time resolution is achieved '
		 + ' by reading fewer rows of the CCD.</p>'
		 + '<p>The minimum frame time of 0.2 sec corresponds to reading '
		 + ' a subarray of 128 rows.  The maximum time of 3.2 sec corresponds to reading all 1024 rows.</p>'
		 + '<p>Any value from 0.2 to 3.2 sec is possible by adjusting the number '
		 + ' of rows to be read AND by accepting a deadtime for frametimes less than 0.4s.</p> '
		 + '<p>The number of rows to be read and the Subarray '
		 + 'Frame Time should be equivalent; the two values will be compared to see that they are.</p> '
		 + '<p>The equation for calculating the Frame Time from the number of '
		 + ' rows to be read is included in the Proposers Guide.</p>'
		 + '<p><font color=green>Value Ranges: NULL, 0 to 10 </font></p>' ;
		
var duty_cycle = '<font color=blue><b>Duty Cycle</b></font><br />'
		 + '<font color=#008080>duty_cycle (acisparam)</font><br />'
		 + '<p>Alternating Exposure Readout: Logical value indicating use of '
		 + 'alternating exposure readout.  The default is "N".  Alternating '
		 + 'Exposure Readout observation sets the number of SECONDARY '
		 + 'exposures that will follow each primary exposure.</p>'
         + '<p>  A deadtime'
		 + 'will result from the short exposure since the electronics still '
		 + 'require 3.2 sec to process full frame.  Therefore, to minimize '
		 + 'the deadtime, the number of short exposures should be kept to a minimum.</p>'
		 + '<p>If Y is selected, Tprimary must be filled.</p>'
		 + '<p><font color=green>Value Ranges: NULL, Y, N </font></p>' ;
		
var secondary_exp_count = '<font color=blue><b>Number</b></font><br />'
		 + '<font color=#008080>secondary_exp_count (acisparam)</font><br />'
		 + '<p>Alternating Exposure Readout: The number of secondary '
		 + ' exposures that will follow each primary exposure.</p>'
		 + '<p>If n = 0, only primary exposures are used. '
		 + 'Read the ACIS chapter of the Proposers Guide for an estimate of the efficiency. '
		 + 'The recommended value is 2.</p>'
		 + '<p><font color=green>Value Ranges: 0 to 15</font></p>';
		
var primary_exp_time = '<font color=blue><b>Tprimary</b></font><br />'
		 + '<font color=#008080>primary_exp_time (acisparam)</font><br />'
		 + '<p>Alternating Exposure Readout: Exposure Time for Primary Cycle: '
		 + 'The primary exposure time in tenths of seconds.  The recommended time for '
		 + 'a non-zero number of secondary exposures is 0.3.</p>'
		 + '<p><font color=green>Value Ranges: NULL, 0 to 10 </font></p>';
		
var secondary_exp_time = '<font color=blue><b>Tsecondary</b></font><br />'
		 + '<font color=#008080>secondary_exp_time (acisparam)</font><br />'
		 + '<p>Alternating Exposure Readout : Exposure Time for Secondary Cycle: '
		 + 'The secondary exposure time in tenths of seconds.  The recommended time for '
	  	 + 'a non-zero number of secondary exposures is 3.2</p>';

var onchip_sum = '<font color=blue><b>Onchip Summing</b></font><br />'
		 + '<font color=#008080>onchip_sum (acisparam)</font><br />'
		 + '<p>Logical value indicating on-chip summation. The default value '
		 + 'is "N".  On-chip summation can be used to reduce the number of '
		 + ' items per CCD readout.</p><p>  The spatial resolution is degraded as '
		 + 'is the event splitting information. Currently, only 2x summation '
		 + 'is supported. You can optionally fill Rows and Column '
	     + '<p>If this is other than 2, expect to be contract by CDO.</p>'
		 + '<p><font color=green>Value Ranges: NULL, N, Y</font></p>';

var onchip_row_count = '<font color=blue><b>Rows</b></font><br />'
		 + '<font color=#008080>onchip_row_count (acisparam)</font><br />'
		 + '<p># of rows for On-Chip Summing.</p> '
		 + '<p><font color=green>Value Ranges: 1 to 512</font></p>';
		
var onchip_column_count = '<font color=blue><b>Columns</b></font><br />'
		 + '<font color=#008080>onchip_column_count (acisparam)</font><br />'
		 + '<p># of columns for On-Chip Summing.</p>'
		 + '<p><font color=green>Value Ranges: 1 to 512</font></p>';
		
var eventfilter = '<font color=blue><b>Energy Filter</b></font><br />'
		 + '<font color=#008080>eventfilter (acisparam)</font><br />'
		 + '<p>This logical value indicates that the user wishes to filter every '
		 + 'candidate event before packing into the telemetry stream.</p> '
		 + '<p> The filter applies to all of the active CCDs.  The use of an '
		 + 'event filter does NOT affect pulse pileup, but only reduces '
		 + 'the telemetry. If Y is selected, Lowest Energy and Energy Range must be filled.</p>'
		 + '<p><font color=green>Value Ranges: NULL, Y, N </font></p>';
		

var multiple_spectral_lines = '<font color=blue><b>Multiple Spectral Line</b></font><br />'
		 + '<font color=#008080>multiple_spectral_lines (acisparam)</font><br />'
		 + '<p>Logical value indicating whether or not more than 2 resolved spectral lines '
		 + 'are expected in the brightest spectrum to be analyzed from this observation.</p> '
		 + '<p>"Y" or "N" is required  for any ACIS-I non-grating observation. Both the two '
		 + 'questions above are asked to trigger assessment of the sensitivity '
		 + 'of ACIS-I imaging observations to gain calibration.</p><p> Science from high S/N ACIS-I '
		 + 'imaging spectroscopy (no gratings) with rich spectra may be affected by '
		 + 'thermally-induced gain drifts.</p>'
		 + '<p><font color=green>Value Ranges: NULL, N, Y</font></p>';

var spectra_max_count = '<font color=blue><b>Spectra Max Count</b></font><br />'
		 + '<font color=#008080>spectra_max_count (acisparam)</font><br />'
		 + '<p>Total maximum expected number of counts for any spectrum to be scientifically '
		 + 'analyzed from this observation. Input is required for any ACIS-I non-grating '
		 + 'observation. </p>'
		 + '<p><font color=green>Value Ranges: NULL, 1 to  100000</font></p>';

var eventfilter_lower = '<font color=blue><b>Energy Lower</b></font><br />'
		 + '<font color=#008080>eventfilter_lower (acisparam)</font><br />'
		 + '<p>Energy Filter: Lower Event Threshold: '
		 + 'The value of the threshold that will be applied.  Units are keV. '
		 + 'If it is not NULL, Event filter must be Y.</p>'
		 + '<p><font color=green>Value Ranges: NULL, 0.0 to 15.0 </font></p>';
		
var eventfilter_higher = '<font color=blue><b>Range</b></font><br />'
		 + '<font color=#008080>eventfilter_higher (acisparam)</font><br />'
         + '<p>The range of the events above the lower threshold which will not be '
		 + 'filtered (in keV).</p><p> (Example: to set an Energy filter from '
         + '0.1- 13 keV as suggested for VF mode.  Set Lower= 0.1 and range=12.9)</p>'
		 + '<p><font color=red>In many configurations, '
         + 'an Energy Range above 13 keV will risk telemetry saturation.</font></p> '
		 + '<p>If it is not NULL, Event filter must be Y.</p>'
		 + '<p><font color=green>Value Ranges: 0.0 to 15.0 </font></p>';
		
var spwindow = '<font color=blue><b>Window Filter</b></font><br />'
		 + '<font color=#008080>spwindow_flag (target)</font><br />'
   		 + '<p>By setting this field to "Y", the user can specify one or more spatial '
   		 + 'window filters -- rectangular regions on specific chips -- within which '
   		 + 'event candidates can be rejected according to their energy or to their '
   		 + 'frequency of occurrence. The use of spatial windows does <i>not</i> affect '
   		 + 'the way the CCD is read out, so there will be no impact on event pile-up. '
   		 + 'Spatial windows will reduce the telemetry volume by removing event  '
		 + 'candidates.</p>'
   		 + '<p>As many as six spatial windows may be specified for each chip. If windows '
   		 + 'overlap, the order in which they are defined in the RPS form is important: '
   		 + 'for each event candidate centered at (CHIPX=<i>x</i>, CHIPY=<i>y</i>), the '
   		 + 'on-board software examines all spatial windows defined for that chip, '
   		 + '<i>in the order specified in the RPS form, lowest index first</i>, and '
   		 + 'decides whether to reject the event based on the parameters in the  '
		 + '<i>first</i> window that contains that (<i>x,y</i>).</p> '
		 + '<p>If the event lies outside all windows, it will not be rejected '
		 + 'by the window filter.</p> '
		 + '<p>If Y is selected, additional fields (Chip, Photon Inclusion, Start Row, '
		 + ' Start Column, Height, Width, Lowest Energy, Energy Range, Sample Rate, '
		 + ' Bias, Bias Frequency, Bias After) are valid</p>'
		 + '<p><font color=green>Value Ranges: NULL, Y, N </font></p>';
		
var ordr = '<font color=blue><b>Rank</b></font><br />'
		 + '<font color=#008080>ordr (aciswin)</font><br />'
         + '<p>It is possible to have multiple windows.  With '
         + 'this keyword you can create addition windows or change '
         + 'the order among existing windows.</p> '
         + '<p>  If you increase this value, numbers of input windows for '
		 + 'Chip, Photon Inclusion, Start Row, Start Column, Height, Width, '
		 + 'Lowest Energy, Energy Range, Sample Rate, Bias, Bias Frequency, Bias After '
		 + 'are also increased.</p> '
		 + '<p><font color=green>Value Ranges: > 1</font></p>';
		
var chip = '<font color=blue><b>Chip</b></font><br />'
		 + '<font color=#008080>chip (asicswin)</font><br /></font><br />'
		 + '<p>Spatial Window. A chip name affected by this acis winodow constraint.</p>'
		 + '<p><font color=green>Value Ranges: NULL, I0, I1, I2, I3, S0, S1, S2, S3, S4, S5</font></p>';

var include_flag = '<font color=blue><b>Photon Inclusion</b></font><br />'
		 + '<font color=#008080>include_flag (asicswin)</font><br /></font><br />'
		 + '<p> Spatial Window. A flag indicating whether the area defined below is included (I), or excluded (E). </p>'
		 + '<p><font color=green>Value Ranges: NULL, I, E/Exclude only after AO9</font></p>';
		
var spwindow_start_row = '<font color=blue><b>Start Row</b></font><br />'
		 + '<font color=#008080>start_row (asicswin)</font> <br />'
		 + '<p> Spatial Window. Starting row: The starting row that will be read.</p>'
		 + '<p><font color=green>Value Ranges: 0 to 895</font></p>';
		
var spwindow_start_column = '<font color=blue><b>Start Column</b></font><br />'
		 + '<font color=#008080>start_column (asicswin)</font> <br />'
		 + '<p>Spatial Window: Starting column: The starting column that will be read.</p>'
		 + '<p><font color=green>Value Ranges:  0 to 895</font></p>';
		
var spwindow_height = '<font color=blue><b>Height</b></font><br />'
		 + '<font color=#008080>height (asicswin)</font> <br />'
		 + '<p>Spatial Window: Height of Window: The number of rows of the window that will be read.</p>'
		 + '<p><font color=green>Value Ranges: 128 to  1023</font></p>';
		
var spwindow_width = '<font color=blue><b>Width</b></font><br />'
		 + '<font color=#008080>width (asicswin)</font> <br />'
		 + '<p>Spatial Window: Width of Window: The number of columns of the window that will be read.</p> '
		 + '<p><font color=green>Value Ranges: 128 to 1023</font></p>';
		
var spwindow_lower_threshold = '<font color=blue><b>Lowest Energy</b></font><br />'
		 + '<font color=#008080>lower_threshold (asicswin)</font> <br />'
         + '<p>The value for the lower discrimination threshold. '
         + 'Units are keV. <b>This keyword only has meaning '
         + 'within th context of a spatial filter,</b> '
         + 'otherwise use the ENERGY FILTER.</p>'
		 + '<p><font color=green>Value Ranges: 0.0 to 15.0</font></p>';
		
var spwindow_pha_range = '<font color=blue><b>Energy Range</b></font><br />'
		 + '<font color=#008080>pha_range (asicswin) </font> <br />'
 		 + '<p>Energy Range for Window: The value for the energy range. '
         + 'Units are keV.  <b>This keyword only has meaning '
         + 'within the context of a spatial filter, </b>'
         + 'otherwise use the ENERGY FILTER.</p>'
		 + '<p><font color=red>In many configurations, an Energy Range above 13 keV '
         + ' will risk telemetry saturation,</font> '
		 + '<p><font color=green>Value Ranges: 0.0 to 15.0</font></p>';
		
var spwindow_sample = '<font color=blue><b>Sample Rate</b></font><br />'
		 + '<font color=#008080>sample (asicswin)</font> <br />'
		 + '<p>Spatial Window: Sampling Rate: The value for the window readout rate. '
		 + 'A value of "1" indicates that every event will be read.  A value of '
		 + '"2"  means that every 2nd event will be read, etc. </p>'
		 + '<p><font color=green>Value Ranges: 1 to 512</font></p>';
		
var bias_request = '<font color=blue><b>Bias</b></font><br />'
		 + '<font color=#008080>bias_request (acisparam)</font><br />'
		 + '<p>Spatial Window: To request a bias different from normal.</p> '
		 + '<p><font color=green>Value Ranges:  N (after AO9) </font></p>';
		
var frequency = '<font color=blue><b>Bias Frequency</b></font><br />'
		 + '<font color=#008080>frequency(acisparam)</font><br />'
		 + '<p>Spatial Window: Designates how often to check the bias.</p>'
		 + '<p><font color=green>Value Ranges: NULL, 0 to 1</font></p>';
		
var bias_after = 'Bias After</b></font><br />'
		 + '<font color=#008080>bias_after(acisparam)</font><br />'
		 + '<p.Spatial Window: The algorithm used for checking the bias.</p>'
		 + '<p><font color=green>Value Ranges: NULL, Y, N</font></p>';
		
var too_id = '<font color=blue><b>TOO ID</b></font><br />'
		 + '<font color=#008080>tooid (too)</font><br />'
		 + '<p>TOO observation ID.</p>';

var too_trig = '<font color=blue><b>TOO Trigger</b></font><br />'
		 + '<font color=#008080>too_trig (too)</font><br />'
		 + '<p>Conditions what trigger this TOO observation.</p>';

var too_type = '<font color=blue><b>TOO Type</b></font><br />'
		 + '<font color=#008080>too_type (too)</font><br />'
         + '<p>TOO Type describes the general lag interval '
         + 'in which the observation can be done after submission '
         + '(categories: 0-4days, 4-12days, 12-30days, >30days) -'
		 + 'before AO 4 the options were just "fast" or "slow".</p>'

var too_start = '<font color=blue><b>Start</b></font><br />'
		 + '<font color=#008080>too_start (too)</font><br />'
		 + '<p>A TOO observation start time.</p>';

var too_stop = '<font color=blue><b>Stop</b></font><br />'
		 + '<font color=#008080>too_stop (too)</font><br />'
		 + '<p>A TOO observation stop time.</p>';

var too_followup =  '<font color=blue><b># of Follow-up Observations</b></font><br />'
		 + '<font color=#008080>too_followup (too)</font><br />'
		 + '<p>Numbers of follow up observation for this TOO event.</p>';

var too_remarks = '<font color=blue><b>TOO Remarks</b></font><br />'
		 + '<font color=#008080>too_remarks (too)</font><br />'
		 + '<p>A remarks for this TOO observation.</p>';

var remarks = '<font color=blue><b>Remarks</b></font><br />'
		 + '<font color=#008080>remarks (target)</font><br />'
		 + '<p>The remark area is  reservered  for constraints with when '
		 + 'Constraints in Remarks? is Y, or  actions/considerations that '
		 + 'apply to the observation. All other remarks should be written in comment area.</p>';

var comments = '<font color=blue><b>Comments</b></font><br />'
		 + '<font color=#008080>comments (target)</font><br />'
		 + '<p>This area is kept as a record of why a change was made. Comments here are '
		 + 'read by Ocat staff. But if the comment impact the observation, contact '
		 + 'CDO for follow through.</p>'
		 + '<p><font color=red> Request for CDO approval must be written in here.</font></p>';


function WindowOpen(name){

        var new_window =
                window.open("","name","height=480,width=400,scrollbars=yes,resizable=yes","true");

        new_window.document.writeln('<html><head><title>Ocat Data Page Parameter Description</title></head><body style="background-color:#FFFFE0">');
        new_window.document.write(name);
        new_window.document.writeln('</body></html>');
	    new_window.document.close();
        new_window.focus();
}


function WindowOpen2(file){
        var toolWindow = 
            window.open("","displayname","toolbar=no,directories=no,menubar=no,location=no,scrollbars=no,status=no,width=950,height=1000,resize=yes");

        toolWindow.document.write("<!DOCTYPE html><html><head><title>Other Tools</title></head>");
        toolWindow.document.write("<body bgcolor='white'>");
        toolWindow.document.write("<iframe src='"+file+"' border=0 width=900 height=1000></iframe>")
        toolWindow.document.write("</body></html>")
        toolWindow.document.close();
        toolWindow.focus();
}

function WindowOpen3(file){
        var seqlWindow = 
            window.open("","displayname","toolbar=no,directories=no,menubar=no,location=no,scrollbars=yes,status=no,width=1200,height=1000,resize=yes");

        seqlWindow.document.write("<!DOCTYPE html><html><head><title>Other Tools</title></head>");
        seqlWindow.document.write("<body bgcolor='white'>");
        seqlWindow.document.write("<iframe src='"+file+"' border=0 width=1200 height=1000></iframe>")
        seqlWindow.document.write("</body></html>")
        seqlWindow.document.close();
        seqlWindow.focus();
}

function WindowOpen4(file){
        var toolWindow = 
            window.open("","displayname","toolbar=yes,directories=no,menubar=no,location=no,scrollbars=no,status=no,width=950,height=1000,resize=yes");

        toolWindow.document.write("<!DOCTYPE html><html><head><title>Other Tools</title></head>");
        toolWindow.document.write("<body bgcolor='white'>");
        toolWindow.document.write("<iframe src='"+file+"' border=0 width=900 height=1000></iframe>")
        toolWindow.document.write("</body></html>")
        toolWindow.document.close();
        toolWindow.focus();
}

