#!/usr/bin/perl 

open(FH, './test_out2');
@save = ();
while(<FH>){
    chomp $_;
    push(@save, $_);
}
close(FH);

open(OUT, '> test_out4');
foreach $ent (@save){
    $out = 'org_'."$ent";
    print OUT "$out\n";
}
foreach $ent (@save){
    $out = 'req_'."$ent";
    print OUT "$out\n";
}

close(OUT);

