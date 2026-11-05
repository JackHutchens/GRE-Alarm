Add-Type -AssemblyName presentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open([System.Uri]"$PSScriptRoot\..\audio_samples\100 Ways To Love A Cat Ways 1-100.mp3")
Start-Sleep -Milliseconds 1200
Write-Host "Duration: $($player.NaturalDuration)"
$player.Close()
