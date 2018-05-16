#!/usr/bin/perl 

open(FH, "ocat_name_table");
open(OUT, '>./test_out');
while(<FH>){
    chomp $_;
    if($_ =~ /#/){
        next;
    }
    @atemp = split(/:/, $_);
    @btemp = split('\,', $atemp[1]);
    foreach $ent (@btemp){
        $ent =~ s/^\s+|\s+$//g ;
        print OUT "$ent\n";
    }
}
close(OUT);
close(FH);
