#!/usr/bin/perl 

open(FH, "changable_param_list");
open(OUT, '>./test_out2');
while(<FH>){
    chomp $_;
    if($_ =~ /#/){
        next;
    }
    @atemp = split(/::/, $_);
    $ent = $atemp[0];
    $ent =~ s/^\s+|\s+$//g ;
    print OUT "$ent\n";
}
close(OUT);
close(FH);
