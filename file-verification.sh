if [ "${file}"="0" ]; then
    echo 'No file provided'
else
    curl -v http://10.10.10.11:30000/repository/scala-test-reports/spark/${file} > ${file}
    python3 comparison-file-check.py ${file}
echo 'python3 main.py ${number} ${file}' > transformation.sh
chmod 777 transformation.sh