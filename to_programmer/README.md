# tools 

## reference

### Textgrid
 - [tgt git](https://github.com/hbuschme/TextGridTools)
 - [tgt doc](https://textgridtools.readthedocs.io/en/stable/api.html)
### Praat
 - [script doc](https://www.fon.hum.uva.nl/praat/manual/Scripting.html)
 - [小狐狸簡介](http://yhhuang1966.blogspot.com/2019/12/praat_9.html)
 - [parselmouth github](https://github.com/YannickJadoul/Parselmouth)
 - [parselmouth doc](https://parselmouth.readthedocs.io/en/stable/)


## sh file
  - get_duration_wavfolder.sh: calculate total duration of audio file (mp3, wav) in given directory
  `./get_duration_wavfolder.sh <wav folder>`


## python3 scripts
  - tools: use `-h`  or `--help` for more info
    - audacitytxt_to_textgrid.py: convert audacity txt file to textgrid format
         `python audacity_txt_to_textgrid.py input_folder`
    - gen_textgrid_and_segment.py: segment wav by silence and generate annotation textgrid files
         `python gen_textgrid_by_scp.py wav.scp output_folder -s 0.5`
    - gen_textgrid_by_scp.py: generate annotation textgrid files by wav.scp
         `python gen_textgrid_by_scp.py wav.scp output_folder -t text`
    - textgrid_count.py: count annotate infomation, some function are not completely implement XD
         `python textgrid_count.py input_folder`

  - test files:
    - praat_textgrid_methods.py
    
  - library:
    - textgrid_lib.py
    - utils.py
