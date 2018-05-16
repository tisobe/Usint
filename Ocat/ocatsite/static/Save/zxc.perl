#!/usr/bin/perl 

open(FH, "table_name_list");
@plist = ();
@dlist = ();
while(<FH>){
    chomp $_;
    @atemp = split(/::/, $_);
    push(@plist, $atemp[1]);
    push(@dlist, $atemp[0]);
    
}
close(FH);

open(FH, "changable_param_list");
while(<FH>){
    chomp $_;
    @atemp = split(//, $_);
    if($atemp[0] eq '#'){
        print "$_\n";
    }else{
        $i = 0;
        foreach $comp (@plist){
            if($_ eq $comp){
                print "$comp".'::'."$dlist[$i]\n";
                last;
            }
            $i++;
        }
    }
}
close(FH);
