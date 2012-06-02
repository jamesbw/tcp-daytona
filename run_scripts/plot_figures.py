import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--max_duration',
                    help="Max duration of trace",
                    required=False,
                    default=0.7,
                    dest="max_duration")




args = parser.parse_args()

alpha = 0.5


def parse_dump(dump_file):

    timestamps = []
    seqnos = []

    with open(dump_file) as f:
        lines = f.readlines()
        start = 0
        for line in lines:
            comma_split = line.split(", ")
            try:
                if comma_split[2] != "ack 1":
                    continue
                if start == 0:
                    start = float(comma_split[0].split(" ")[0])
                timestamp = float(comma_split[0].split(" ")[0]) - start
                if timestamp > args.max_duration:
                    continue
                seqnos += [int(comma_split[1].split(":")[1])]
                timestamps += [timestamp]
            except:
                print "%s" % comma_split
                continue

    print len(timestamps), len(seqnos)

    return timestamps, seqnos

timestamps_baseline, seqnos_baseline = parse_dump("sender.dump.baseline")
timestamps_ack_division, seqnos_ack_division = parse_dump("sender.dump.ack_division")
timestamps_ack_duplication, seqnos_ack_duplication = parse_dump("sender.dump.ack_duplication")





#figure 4
plt.clf()
plt.scatter(timestamps_baseline, seqnos_baseline, label="Not misbehaving", color = "blue", alpha = alpha)
plt.scatter(timestamps_ack_division, seqnos_ack_division, label="Ack division", color= "red", alpha = alpha)
plt.title("TCP Daytona: Ack division (figure 4)")
plt.ylabel("Sequence numbers")
plt.grid()
plt.legend(loc='upper left')
plt.xlabel("Time (s)")
plt.ylim((0,max(seqnos_baseline + seqnos_ack_division)))
print "Ack division plot saved as %s" % "ack_division_plot.png"
plt.savefig("../ack_division_plot.png")
plt.show()


#figure 5
plt.clf()
plt.scatter(timestamps_baseline, seqnos_baseline, label="Not misbehaving", color = "blue", alpha = alpha)
plt.scatter(timestamps_ack_duplication, seqnos_ack_duplication, label="Ack duplication", color="red", alpha = alpha)
plt.title("TCP Daytona: Ack duplication (figure 5)")
plt.ylabel("Sequence numbers")
plt.grid()
plt.legend(loc='upper left')
plt.xlabel("Time (s)")
plt.ylim((0,max(seqnos_baseline + seqnos_ack_duplication)))
print "Ack duplication plot saved as %s" % "ack_duplication_plot.png"
plt.savefig("../ack_duplication_plot.png")
plt.show()





