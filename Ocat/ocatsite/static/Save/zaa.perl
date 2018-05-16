#!/usr/bin/perl 

$line = 'This ACIS observation will require the following adjustments before it can be scheduled: 1) The use of a non-standard dither amplitude of 1 arcsec, however the frequency and phase can be set to default values. 2) The detector and subarray offsets may/will need to be adjusted for to prevent the pulsar from landing on the same ACIS pixels when compared to its history. (Contact Paul Plucinsky).';

$line = 'Pre-Planned Target of Opportunity (ToO) Observations of the Crab Nebula upon the Occurrence of the Next Gamma-Ray Flare ';
@test = split(//, $line);
$cnt = 0;
foreach (@test){
    $cnt++;
}
print "$cnt\n";
