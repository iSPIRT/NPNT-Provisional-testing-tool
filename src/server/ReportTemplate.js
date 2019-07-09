
module.exports = ({ testId, droneId, email, test, result }) => {
    const today = new Date();
    return `
    <p style="text-align: center;">Test Report</p>
<p style="text-align: left;">Date: ${`${today.getDate()}. ${today.getMonth() + 1}. ${today.getFullYear()}.`}</p>
<p style="text-align: left;">Test ID: ${testId}</p>
<p style="text-align: left;">Drone ID: ${droneId}</p>
<p style="text-align: left;">Email: ${email}</p>
<p style="text-align: center;">Results</p>
<table width="100%">
<tbody>
<tr>
<td>Testcase</td>
<td>Description</td>
<td>Result</td>
</tr>
<tr>
<td>&nbsp;</td>
<td>&nbsp;</td>
<td>&nbsp;</td>
</tr>
<tr>
<td>Testcase 1</td>
<td>${test[0]}</td>
<td>${result[0]}</td>
</tr>
<tr>
<td>Testcase 2</td>
<td>${test[1]}</td>
<td>${result[1]}</td>
</tr>
<tr>
<td>Testcase 3</td>
<td>${test[2]}</td>
<td>${result[2]}</td>
</tr>
<tr>
<td>Testcase 4</td>
<td>${test[3]}</td>
<td>${result[3]}</td>
</tr>
<tr>
<td>Testcase 5</td>
<td>${test[4]}</td>
<td>${result[4]}</td>
</tr>
</tbody>
</table>
    `;
};