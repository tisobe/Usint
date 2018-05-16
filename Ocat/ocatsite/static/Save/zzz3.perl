#!/usr/bin/perl 

open(FH, './test_out2');
@save = ();
while(<FH>){
    chomp $_;
    push(@save, $_);
}
close(FH);

open(OUT, '> test_out3');
foreach $ent (@save){

    $tab = count();

    $out = 'org_'."$ent";
    for($i = 0; $i < $tab; $i++){
        $out = $out."\t";
    }

    $out = $out.'= models.CharField(max_length=20)';
    print OUT "\t$out\n";
}
foreach $ent (@save){

    $tab = count();

    $out = 'req_'."$ent";
    for($i = 0; $i < $tab; $i++){
        $out = $out."\t";
    }

    $out = $out.'= models.CharField(max_length=20)';
    print OUT "\t$out\n";
}

close(OUT);




sub count{

    $cnt = 0;
    $test = split(//, $ent);
    $diff = 24 - $test;
    $tab  = int($diff / 4);
    if($diff != 4.0 * $tab){
        $tab += 1;
    }
    
    return $tab;
}
   
