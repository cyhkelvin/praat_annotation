dir=$1

sec=0
wav_num=$(find $dir -name *wav|wc -l)
if [ $wav_num -gt 0 ]; then
  for wav in $(ls $dir/*wav); do
    wav_sec=$(soxi $wav|grep Duration|awk -F '=' '{print $1}'|awk -F ':' '{print $2*3600+$3*60+$4}')
    sec=$(echo "$wav_sec $sec"|awk '{print $1+$2}')
  done
fi

mp3_num=$(find $dir -name *mp3|wc -l)
if [ $mp3_num -gt 0 ]; then
  for mp3 in $(ls $dir/*mp3); do
    mp3_sec=$(soxi $mp3|grep Duration|awk -F '=' '{print $1}'|awk -F ':' '{print $2*3600+$3*60+$4}')
    sec=$(echo "$mp3_sec $sec"|awk '{print $1+$2}')
  done
fi

if [ $wav_num -eq 0 ] && [ $mp3_num -eq 0 ]; then
  echo "file format is not mp3/wav."
else
  printf "%s: %s sec / %.2f hr\n" $dir $sec $(echo $sec|awk '{print $sec/3600}')
fi

