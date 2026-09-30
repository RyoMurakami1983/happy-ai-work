param([switch]$List, [switch]$Run, [switch]$Short)
if ($List) {
    if ($Short) { 'short: isolated arithmetic regression; synthetic; estimate <1 second' }
    else { 'full: isolated arithmetic regression + synthetic soak; estimate 8 minutes; budget 10 minutes; fixture emulates execution immediately, no load' }
} elseif ($Run) {
    if ((2 + 2) -ne 4) { throw 'arithmetic failed' }
    'PASS: synthetic fixture emulation only; no real soak or environment compatibility measured'
}
