export SILENT=1

python main.py ./input_data/a_an_example.in.txt &
python main.py ./input_data/b_better_start_small.in.txt &
python main.py ./input_data/c_collaboration.in.txt &
python main.py ./input_data/d_dense_schedule.in.txt &
python main.py ./input_data/e_exceptional_skills.in.txt &
python main.py ./input_data/f_find_great_mentors.in.txt &

wait
