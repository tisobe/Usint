from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


# Create your models here.

class UserProfile(models.Model):
    """
    adding fields to admin user
    """
    user   = models.ForeignKey(User, unique=True)
    office = models.CharField(max_length=20, blank=True)
    cell   = models.CharField(max_length=20, blank=True)
    home   = models.CharField(max_length=20, blank=True)
    duty   = models.CharField(max_length=60, blank=True)

    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    """
    Create the UserProfile when a new User is saved
    """
    if created:
        profile = UserProfile()
        profile.user = instance
        profile.save()


post_save.connect(create_user_profile, sender=User)



class Approved(models.Model):
    """
    save approved observation.
    e.g.: 17686   890115  lpd 06/25/15  + (extra info) 150625
    odate is used to sort the data by date
    """
    obsid = models.CharField(max_length=10)
    seqno = models.CharField(max_length=10)
    poc   = models.CharField(max_length=15)
    date  = models.CharField(max_length=15)
    odate = models.CharField(max_length=10)

    def __unicode__(self):
        return self.obsid

#-----------------------------------------------------

class Updates(models.Model):
    """
    save updates_table.list
    e.g., 16726.001   mccolml 05/27/15    NULL    NULL    brad 05/27/15   401648  brad
            + (extra info) 16726    001 05/27/15 150527
    odate is used to sort the data by date
    """
    obsidrev = models.CharField(max_length=15)
    general  = models.CharField(max_length=20)
    acis     = models.CharField(max_length=20)
    si_mode  = models.CharField(max_length=20)
    verified = models.CharField(max_length=20)
    seqno    = models.CharField(max_length=10)
    poc      = models.CharField(max_length=15)
    obsid    = models.CharField(max_length=10)
    rev      = models.CharField(max_length=10)
    date     = models.CharField(max_length=10)
    odate    = models.CharField(max_length=10)

    def __unicode__(self):
        return self.obsidrev

#-----------------------------------------------------

class Obs_plan(models.Model):
    """
    save obs plan list 
    e.g.: go  201001  16680   unobserved  sjw 16  Oct  9 2016 12:00AM
    odate is used to sort the data by date
    """
    obsid = models.CharField(max_length=10)
    seqno = models.CharField(max_length=10)
    otype = models.CharField(max_length=10)
    status= models.CharField(max_length=10)
    poc   = models.CharField(max_length=15)
    ao    = models.CharField(max_length=10)
    date  = models.CharField(max_length=15)
    odate = models.CharField(max_length=10)

    def __unicode__(self):
        return self.obsid

#-----------------------------------------------------

class Data_tables(models.Model):
    """
    save all modifiable parameters (plus several others) for original and 
    reqeuested cases.
    """
    obsidrev                    = models.CharField(max_length=15, blank=True)
    obsid                       = models.CharField(max_length=10, blank=True)
    targid                      = models.CharField(max_length=10, blank=True)
    seq_nbr                     = models.CharField(max_length=15, blank=True)
    prop_num                    = models.CharField(max_length=20, blank=True)
    targname                    = models.CharField(max_length=40, blank=True)
    title                       = models.CharField(max_length=200, blank=True)
    poc                         = models.CharField(max_length=10, blank=True)
    asis                        = models.CharField(max_length=10, blank=True)
    rev                         = models.CharField(max_length=10, blank=True)
    date                        = models.CharField(max_length=10, blank=True)
    odate                       = models.CharField(max_length=10, blank=True)
    org_si_mode					= models.CharField(max_length=15, blank=True)
    org_instrument				= models.CharField(max_length=15, blank=True)
    org_grating					= models.CharField(max_length=15, blank=True)
    org_type					= models.CharField(max_length=15, blank=True)
    org_ra						= models.CharField(max_length=15, blank=True)
    org_dec						= models.CharField(max_length=15, blank=True)
    org_y_det_offset			= models.CharField(max_length=15, blank=True)
    org_z_det_offset			= models.CharField(max_length=15, blank=True)
    org_trans_offset			= models.CharField(max_length=15, blank=True)
    org_focus_offset			= models.CharField(max_length=15, blank=True)
    org_defocus					= models.CharField(max_length=15, blank=True)
    org_raster_scan				= models.CharField(max_length=15, blank=True)
    org_uninterrupt				= models.CharField(max_length=15, blank=True)
    org_extended_src			= models.CharField(max_length=15, blank=True)
    org_obj_flag				= models.CharField(max_length=10, blank=True)
    org_object					= models.CharField(max_length=15, blank=True)
    org_photometry_flag			= models.CharField(max_length=15, blank=True)
    org_vmagnitude				= models.CharField(max_length=15, blank=True)
    org_est_cnt_rate			= models.CharField(max_length=15, blank=True)
    org_forder_cnt_rate			= models.CharField(max_length=15, blank=True)
    org_dither_flag				= models.CharField(max_length=15, blank=True)
    org_y_amp					= models.CharField(max_length=15, blank=True)
    org_z_amp					= models.CharField(max_length=15, blank=True)
    org_y_freq					= models.CharField(max_length=15, blank=True)
    org_z_freq					= models.CharField(max_length=15, blank=True)
    org_y_phase					= models.CharField(max_length=15, blank=True)
    org_z_phase					= models.CharField(max_length=15, blank=True)
    org_window_flag				= models.CharField(max_length=15, blank=True)
    org_time_ordr				= models.CharField(max_length=15, blank=True)
    org_window_constraint1		= models.CharField(max_length=15, blank=True)
    org_tstart1					= models.CharField(max_length=15, blank=True)
    org_tstop1					= models.CharField(max_length=15, blank=True)
    org_window_constraint2		= models.CharField(max_length=15, blank=True)
    org_tstart2					= models.CharField(max_length=15, blank=True)
    org_tstop2					= models.CharField(max_length=15, blank=True)
    org_window_constraint3		= models.CharField(max_length=15, blank=True)
    org_tstart3					= models.CharField(max_length=15, blank=True)
    org_tstop3					= models.CharField(max_length=15, blank=True)
    org_window_constraint4		= models.CharField(max_length=15, blank=True)
    org_tstart4					= models.CharField(max_length=15, blank=True)
    org_tstop4					= models.CharField(max_length=15, blank=True)
    org_window_constraint5		= models.CharField(max_length=15, blank=True)
    org_tstart5					= models.CharField(max_length=15, blank=True)
    org_tstop5					= models.CharField(max_length=15, blank=True)
    org_window_constraint6		= models.CharField(max_length=15, blank=True)
    org_tstart6					= models.CharField(max_length=15, blank=True)
    org_tstop6					= models.CharField(max_length=15, blank=True)
    org_roll_flag				= models.CharField(max_length=10, blank=True)
    org_roll_ordr				= models.CharField(max_length=15, blank=True)
    org_roll_constraint1		= models.CharField(max_length=15, blank=True)
    org_roll_1801				= models.CharField(max_length=15, blank=True)
    org_roll1					= models.CharField(max_length=15, blank=True)
    org_roll_tolerance1			= models.CharField(max_length=15, blank=True)
    org_roll_constraint2		= models.CharField(max_length=15, blank=True)
    org_roll_1802				= models.CharField(max_length=15, blank=True)
    org_roll2					= models.CharField(max_length=15, blank=True)
    org_roll_tolerance2			= models.CharField(max_length=15, blank=True)
    org_roll_constraint3		= models.CharField(max_length=15, blank=True)
    org_roll_1803				= models.CharField(max_length=15, blank=True)
    org_roll3					= models.CharField(max_length=15, blank=True)
    org_roll_tolerance3			= models.CharField(max_length=15, blank=True)
    org_roll_constraint4		= models.CharField(max_length=15, blank=True)
    org_roll_1804				= models.CharField(max_length=15, blank=True)
    org_roll4					= models.CharField(max_length=15, blank=True)
    org_roll_tolerance4			= models.CharField(max_length=15, blank=True)
    org_roll_constraint5		= models.CharField(max_length=15, blank=True)
    org_roll_1805				= models.CharField(max_length=15, blank=True)
    org_roll5					= models.CharField(max_length=15, blank=True)
    org_roll_tolerance5			= models.CharField(max_length=15, blank=True)
    org_roll_constraint6		= models.CharField(max_length=15, blank=True)
    org_roll_1806				= models.CharField(max_length=15, blank=True)
    org_roll6					= models.CharField(max_length=15, blank=True)
    org_roll_tolerance6			= models.CharField(max_length=15, blank=True)
    org_constr_in_remarks		= models.CharField(max_length=15, blank=True)
    org_phase_constraint_flag	= models.CharField(max_length=10, blank=True)
    org_phase_epoch				= models.CharField(max_length=15, blank=True)
    org_phase_period			= models.CharField(max_length=15, blank=True)
    org_phase_start				= models.CharField(max_length=15, blank=True)
    org_phase_start_margin		= models.CharField(max_length=15, blank=True)
    org_phase_end				= models.CharField(max_length=15, blank=True)
    org_phase_end_margin		= models.CharField(max_length=15, blank=True)
    org_group_id				= models.CharField(max_length=15, blank=True)
    org_monitor_flag			= models.CharField(max_length=10, blank=True)
    org_pre_id      			= models.CharField(max_length=10, blank=True)
    org_pre_min_lead			= models.CharField(max_length=15, blank=True)
    org_pre_max_lead			= models.CharField(max_length=15, blank=True)
    org_multitelescope			= models.CharField(max_length=15, blank=True)
    org_observatories			= models.CharField(max_length=15, blank=True)
    org_multitelescope_interval	= models.CharField(max_length=15, blank=True)
    org_hrc_config				= models.CharField(max_length=15, blank=True)
    org_hrc_zero_block			= models.CharField(max_length=10, blank=True)
    org_timing_mode				= models.CharField(max_length=10, blank=True)
    org_hrc_si_mode				= models.CharField(max_length=15, blank=True)
    org_exp_mode				= models.CharField(max_length=10, blank=True)
    org_bep_pack				= models.CharField(max_length=10, blank=True)
    org_frame_time				= models.CharField(max_length=15, blank=True)
    org_most_efficient			= models.CharField(max_length=10, blank=True)
    org_standard_chips			= models.CharField(max_length=15, blank=True)
    org_ccdi0_on				= models.CharField(max_length=10, blank=True)
    org_ccdi1_on				= models.CharField(max_length=10, blank=True)
    org_ccdi2_on				= models.CharField(max_length=10, blank=True)
    org_ccdi3_on				= models.CharField(max_length=10, blank=True)
    org_ccds0_on				= models.CharField(max_length=10, blank=True)
    org_ccds1_on				= models.CharField(max_length=10, blank=True)
    org_ccds2_on				= models.CharField(max_length=10, blank=True)
    org_ccds3_on				= models.CharField(max_length=10, blank=True)
    org_ccds4_on				= models.CharField(max_length=10, blank=True)
    org_ccds5_on				= models.CharField(max_length=10, blank=True)
    org_subarray				= models.CharField(max_length=10, blank=True)
    org_subarray_start_row		= models.CharField(max_length=15, blank=True)
    org_subarray_row_count		= models.CharField(max_length=15, blank=True)
    org_subarray_frame_time		= models.CharField(max_length=15, blank=True)
    org_duty_cycle				= models.CharField(max_length=10, blank=True)
    org_secondary_exp_count		= models.CharField(max_length=15, blank=True)
    org_primary_exp_time		= models.CharField(max_length=15, blank=True)
    org_secondary_exp_time		= models.CharField(max_length=15, blank=True)
    org_onchip_sum				= models.CharField(max_length=10, blank=True)
    org_onchip_row_count		= models.CharField(max_length=15, blank=True)
    org_onchip_column_count		= models.CharField(max_length=15, blank=True)
    org_eventfilter				= models.CharField(max_length=10, blank=True)
    org_eventfilter_lower		= models.CharField(max_length=15, blank=True)
    org_eventfilter_higher		= models.CharField(max_length=15, blank=True)
    org_multiple_spectral_lines	= models.CharField(max_length=10, blank=True)
    org_spectra_max_count		= models.CharField(max_length=15, blank=True)
    org_spwindow_flag			= models.CharField(max_length=10, blank=True)
    org_ordr					= models.CharField(max_length=15, blank=True)
    org_chip1					= models.CharField(max_length=15, blank=True)
    org_start_row1				= models.CharField(max_length=15, blank=True)
    org_start_column1			= models.CharField(max_length=15, blank=True)
    org_height1					= models.CharField(max_length=15, blank=True)
    org_width1					= models.CharField(max_length=15, blank=True)
    org_lower_threshold1		= models.CharField(max_length=15, blank=True)
    org_pha_range1				= models.CharField(max_length=15, blank=True)
    org_sample1					= models.CharField(max_length=15, blank=True)
    org_chip2					= models.CharField(max_length=15, blank=True)
    org_start_row2				= models.CharField(max_length=15, blank=True)
    org_start_column2			= models.CharField(max_length=15, blank=True)
    org_height2					= models.CharField(max_length=15, blank=True)
    org_width2					= models.CharField(max_length=15, blank=True)
    org_lower_threshold2		= models.CharField(max_length=15, blank=True)
    org_pha_range2				= models.CharField(max_length=15, blank=True)
    org_sample2					= models.CharField(max_length=15, blank=True)
    org_chip3					= models.CharField(max_length=15, blank=True)
    org_start_row3				= models.CharField(max_length=15, blank=True)
    org_start_column3			= models.CharField(max_length=15, blank=True)
    org_height3					= models.CharField(max_length=15, blank=True)
    org_width3					= models.CharField(max_length=15, blank=True)
    org_lower_threshold3		= models.CharField(max_length=15, blank=True)
    org_pha_range3				= models.CharField(max_length=15, blank=True)
    org_sample3					= models.CharField(max_length=15, blank=True)
    org_chip4					= models.CharField(max_length=15, blank=True)
    org_start_row4				= models.CharField(max_length=15, blank=True)
    org_start_column4			= models.CharField(max_length=15, blank=True)
    org_height4					= models.CharField(max_length=15, blank=True)
    org_width4					= models.CharField(max_length=15, blank=True)
    org_lower_threshold4		= models.CharField(max_length=15, blank=True)
    org_pha_range4				= models.CharField(max_length=15, blank=True)
    org_sample4					= models.CharField(max_length=15, blank=True)
    org_chip5					= models.CharField(max_length=15, blank=True)
    org_start_row5				= models.CharField(max_length=15, blank=True)
    org_start_column5			= models.CharField(max_length=15, blank=True)
    org_height5					= models.CharField(max_length=15, blank=True)
    org_width5					= models.CharField(max_length=15, blank=True)
    org_lower_threshold5		= models.CharField(max_length=15, blank=True)
    org_pha_range5				= models.CharField(max_length=15, blank=True)
    org_sample5					= models.CharField(max_length=15, blank=True)
    org_chip6					= models.CharField(max_length=15, blank=True)
    org_start_row6				= models.CharField(max_length=15, blank=True)
    org_start_column6			= models.CharField(max_length=15, blank=True)
    org_height6					= models.CharField(max_length=15, blank=True)
    org_width6					= models.CharField(max_length=15, blank=True)
    org_lower_threshold6		= models.CharField(max_length=15, blank=True)
    org_pha_range6				= models.CharField(max_length=15, blank=True)
    org_sample6					= models.CharField(max_length=15, blank=True)
    org_remarks					= models.CharField(max_length=800, blank=True)
    org_comments				= models.CharField(max_length=800, blank=True)
    req_si_mode					= models.CharField(max_length=15, blank=True)
    req_instrument				= models.CharField(max_length=15, blank=True)
    req_grating					= models.CharField(max_length=15, blank=True)
    req_type					= models.CharField(max_length=15, blank=True)
    req_ra						= models.CharField(max_length=15, blank=True)
    req_dec						= models.CharField(max_length=15, blank=True)
    req_y_det_offset			= models.CharField(max_length=15, blank=True)
    req_z_det_offset			= models.CharField(max_length=15, blank=True)
    req_trans_offset			= models.CharField(max_length=15, blank=True)
    req_focus_offset			= models.CharField(max_length=15, blank=True)
    req_defocus					= models.CharField(max_length=15, blank=True)
    req_raster_scan				= models.CharField(max_length=15, blank=True)
    req_uninterrupt				= models.CharField(max_length=15, blank=True)
    req_extended_src			= models.CharField(max_length=15, blank=True)
    req_obj_flag				= models.CharField(max_length=10, blank=True)
    req_object					= models.CharField(max_length=15, blank=True)
    req_photometry_flag			= models.CharField(max_length=10, blank=True)
    req_vmagnitude				= models.CharField(max_length=15, blank=True)
    req_est_cnt_rate			= models.CharField(max_length=15, blank=True)
    req_forder_cnt_rate			= models.CharField(max_length=15, blank=True)
    req_dither_flag				= models.CharField(max_length=10, blank=True)
    req_y_amp					= models.CharField(max_length=15, blank=True)
    req_z_amp					= models.CharField(max_length=15, blank=True)
    req_y_freq					= models.CharField(max_length=15, blank=True)
    req_z_freq					= models.CharField(max_length=15, blank=True)
    req_y_phase					= models.CharField(max_length=15, blank=True)
    req_z_phase					= models.CharField(max_length=15, blank=True)
    req_window_flag				= models.CharField(max_length=10, blank=True)
    req_time_ordr				= models.CharField(max_length=15, blank=True)
    req_window_constraint1		= models.CharField(max_length=15, blank=True)
    req_tstart1					= models.CharField(max_length=15, blank=True)
    req_tstop1					= models.CharField(max_length=15, blank=True)
    req_window_constraint2		= models.CharField(max_length=15, blank=True)
    req_tstart2					= models.CharField(max_length=15, blank=True)
    req_tstop2					= models.CharField(max_length=15, blank=True)
    req_window_constraint3		= models.CharField(max_length=15, blank=True)
    req_tstart3					= models.CharField(max_length=15, blank=True)
    req_tstop3					= models.CharField(max_length=15, blank=True)
    req_window_constraint4		= models.CharField(max_length=15, blank=True)
    req_tstart4					= models.CharField(max_length=15, blank=True)
    req_tstop4					= models.CharField(max_length=15, blank=True)
    req_window_constraint5		= models.CharField(max_length=15, blank=True)
    req_tstart5					= models.CharField(max_length=15, blank=True)
    req_tstop5					= models.CharField(max_length=15, blank=True)
    req_window_constraint6		= models.CharField(max_length=15, blank=True)
    req_tstart6					= models.CharField(max_length=15, blank=True)
    req_tstop6					= models.CharField(max_length=15, blank=True)
    req_roll_flag				= models.CharField(max_length=10, blank=True)
    req_roll_ordr				= models.CharField(max_length=15, blank=True)
    req_roll_constraint1		= models.CharField(max_length=15, blank=True)
    req_roll_1801				= models.CharField(max_length=15, blank=True)
    req_roll1					= models.CharField(max_length=15, blank=True)
    req_roll_tolerance1			= models.CharField(max_length=15, blank=True)
    req_roll_constraint2		= models.CharField(max_length=15, blank=True)
    req_roll_1802				= models.CharField(max_length=15, blank=True)
    req_roll2					= models.CharField(max_length=15, blank=True)
    req_roll_tolerance2			= models.CharField(max_length=15, blank=True)
    req_roll_constraint3		= models.CharField(max_length=15, blank=True)
    req_roll_1803				= models.CharField(max_length=15, blank=True)
    req_roll3					= models.CharField(max_length=15, blank=True)
    req_roll_tolerance3			= models.CharField(max_length=15, blank=True)
    req_roll_constraint4		= models.CharField(max_length=15, blank=True)
    req_roll_1804				= models.CharField(max_length=15, blank=True)
    req_roll4					= models.CharField(max_length=15, blank=True)
    req_roll_tolerance4			= models.CharField(max_length=15, blank=True)
    req_roll_constraint5		= models.CharField(max_length=15, blank=True)
    req_roll_1805				= models.CharField(max_length=15, blank=True)
    req_roll5					= models.CharField(max_length=15, blank=True)
    req_roll_tolerance5			= models.CharField(max_length=15, blank=True)
    req_roll_constraint6		= models.CharField(max_length=15, blank=True)
    req_roll_1806				= models.CharField(max_length=15, blank=True)
    req_roll6					= models.CharField(max_length=15, blank=True)
    req_roll_tolerance6			= models.CharField(max_length=15, blank=True)
    req_constr_in_remarks		= models.CharField(max_length=15, blank=True)
    req_phase_constraint_flag	= models.CharField(max_length=10, blank=True)
    req_phase_epoch				= models.CharField(max_length=15, blank=True)
    req_phase_period			= models.CharField(max_length=15, blank=True)
    req_phase_start				= models.CharField(max_length=15, blank=True)
    req_phase_start_margin		= models.CharField(max_length=15, blank=True)
    req_phase_end				= models.CharField(max_length=15, blank=True)
    req_phase_end_margin		= models.CharField(max_length=15, blank=True)
    req_group_id				= models.CharField(max_length=15, blank=True)
    req_monitor_flag			= models.CharField(max_length=10, blank=True)
    req_pre_id      			= models.CharField(max_length=10, blank=True)
    req_pre_min_lead			= models.CharField(max_length=15, blank=True)
    req_pre_max_lead			= models.CharField(max_length=15, blank=True)
    req_multitelescope			= models.CharField(max_length=15, blank=True)
    req_observatories			= models.CharField(max_length=15, blank=True)
    req_multitelescope_interval	= models.CharField(max_length=15, blank=True)
    req_hrc_config				= models.CharField(max_length=15, blank=True)
    req_hrc_zero_block			= models.CharField(max_length=10, blank=True)
    req_timing_mode				= models.CharField(max_length=10, blank=True)
    req_hrc_si_mode				= models.CharField(max_length=15, blank=True)
    req_exp_mode				= models.CharField(max_length=10, blank=True)
    req_bep_pack				= models.CharField(max_length=10, blank=True)
    req_frame_time				= models.CharField(max_length=15, blank=True)
    req_most_efficient			= models.CharField(max_length=10, blank=True)
    req_standard_chips			= models.CharField(max_length=15, blank=True)
    req_ccdi0_on				= models.CharField(max_length=10, blank=True)
    req_ccdi1_on				= models.CharField(max_length=10, blank=True)
    req_ccdi2_on				= models.CharField(max_length=10, blank=True)
    req_ccdi3_on				= models.CharField(max_length=10, blank=True)
    req_ccds0_on				= models.CharField(max_length=10, blank=True)
    req_ccds1_on				= models.CharField(max_length=10, blank=True)
    req_ccds2_on				= models.CharField(max_length=10, blank=True)
    req_ccds3_on				= models.CharField(max_length=10, blank=True)
    req_ccds4_on				= models.CharField(max_length=10, blank=True)
    req_ccds5_on				= models.CharField(max_length=10, blank=True)
    req_subarray				= models.CharField(max_length=10, blank=True)
    req_subarray_start_row		= models.CharField(max_length=15, blank=True)
    req_subarray_row_count		= models.CharField(max_length=15, blank=True)
    req_subarray_frame_time		= models.CharField(max_length=15, blank=True)
    req_duty_cycle				= models.CharField(max_length=10, blank=True)
    req_secondary_exp_count		= models.CharField(max_length=15, blank=True)
    req_primary_exp_time		= models.CharField(max_length=15, blank=True)
    req_secondary_exp_time		= models.CharField(max_length=15, blank=True)
    req_onchip_sum				= models.CharField(max_length=10, blank=True)
    req_onchip_row_count		= models.CharField(max_length=15, blank=True)
    req_onchip_column_count		= models.CharField(max_length=15, blank=True)
    req_eventfilter				= models.CharField(max_length=10, blank=True)
    req_eventfilter_lower		= models.CharField(max_length=15, blank=True)
    req_eventfilter_higher		= models.CharField(max_length=15, blank=True)
    req_multiple_spectral_lines	= models.CharField(max_length=10, blank=True)
    req_spectra_max_count		= models.CharField(max_length=15, blank=True)
    req_spwindow_flag			= models.CharField(max_length=10, blank=True)
    req_ordr					= models.CharField(max_length=15, blank=True)
    req_chip1					= models.CharField(max_length=10, blank=True)
    req_start_row1				= models.CharField(max_length=15, blank=True)
    req_start_column1			= models.CharField(max_length=15, blank=True)
    req_height1					= models.CharField(max_length=15, blank=True)
    req_width1					= models.CharField(max_length=15, blank=True)
    req_lower_threshold1		= models.CharField(max_length=15, blank=True)
    req_pha_range1				= models.CharField(max_length=15, blank=True)
    req_sample1					= models.CharField(max_length=15, blank=True)
    req_chip2					= models.CharField(max_length=10, blank=True)
    req_start_row2				= models.CharField(max_length=15, blank=True)
    req_start_column2			= models.CharField(max_length=15, blank=True)
    req_height2					= models.CharField(max_length=15, blank=True)
    req_width2					= models.CharField(max_length=15, blank=True)
    req_lower_threshold2		= models.CharField(max_length=15, blank=True)
    req_pha_range2				= models.CharField(max_length=15, blank=True)
    req_sample2					= models.CharField(max_length=15, blank=True)
    req_chip3					= models.CharField(max_length=10, blank=True)
    req_start_row3				= models.CharField(max_length=15, blank=True)
    req_start_column3			= models.CharField(max_length=15, blank=True)
    req_height3					= models.CharField(max_length=15, blank=True)
    req_width3					= models.CharField(max_length=15, blank=True)
    req_lower_threshold3		= models.CharField(max_length=15, blank=True)
    req_pha_range3				= models.CharField(max_length=15, blank=True)
    req_sample3					= models.CharField(max_length=15, blank=True)
    req_chip4					= models.CharField(max_length=10, blank=True)
    req_start_row4				= models.CharField(max_length=15, blank=True)
    req_start_column4			= models.CharField(max_length=15, blank=True)
    req_height4					= models.CharField(max_length=15, blank=True)
    req_width4					= models.CharField(max_length=15, blank=True)
    req_lower_threshold4		= models.CharField(max_length=15, blank=True)
    req_pha_range4				= models.CharField(max_length=15, blank=True)
    req_sample4					= models.CharField(max_length=15, blank=True)
    req_chip5					= models.CharField(max_length=10, blank=True)
    req_start_row5				= models.CharField(max_length=15, blank=True)
    req_start_column5			= models.CharField(max_length=15, blank=True)
    req_height5					= models.CharField(max_length=15, blank=True)
    req_width5					= models.CharField(max_length=15, blank=True)
    req_lower_threshold5		= models.CharField(max_length=15, blank=True)
    req_pha_range5				= models.CharField(max_length=15, blank=True)
    req_sample5					= models.CharField(max_length=15, blank=True)
    req_chip6					= models.CharField(max_length=10, blank=True)
    req_start_row6				= models.CharField(max_length=15, blank=True)
    req_start_column6			= models.CharField(max_length=15, blank=True)
    req_height6					= models.CharField(max_length=15, blank=True)
    req_width6					= models.CharField(max_length=15, blank=True)
    req_lower_threshold6		= models.CharField(max_length=15, blank=True)
    req_pha_range6				= models.CharField(max_length=15, blank=True)
    req_sample6					= models.CharField(max_length=15, blank=True)
    req_remarks					= models.CharField(max_length=800, blank=True)
    req_comments				= models.CharField(max_length=800, blank=True)
    tooid                       = models.CharField(max_length=15, blank=True)
    too_trig                    = models.CharField(max_length=800, blank=True)
    too_type                    = models.CharField(max_length=15, blank=True)
    too_start                   = models.CharField(max_length=15, blank=True)
    too_stop                    = models.CharField(max_length=15, blank=True)
    too_remarks                 = models.CharField(max_length=800, blank=True)
