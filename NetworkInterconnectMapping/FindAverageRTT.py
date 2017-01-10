from GetMeasurements import Get
from FindMedianRTT import FindMedianRTT

class FindAverageRTT(object):

    def __init__(self, measurement_id, probe_id, asn, start, end):
        self.measurement_id = measurement_id
        self.probe_id = probe_id
        self.asn = asn
        # self.target_asn = target_asn
        self.start = start
        self.end = end
        measurements = Get()
        self.same_measurements = measurements.getMeasurementsForAverageRTT(measurement_id, probe_id, asn, start, end)

    def findAverage(self):
        collect_to_calculate_average = []
        average_median_rtt = []
        count = 0
        print self.same_measurements
        for this_result in self.same_measurements:
            rtt_calculation = FindMedianRTT(this_result)
            median_rtt_per_result = rtt_calculation.findMedianRTT()
            collect_to_calculate_average.append(median_rtt_per_result)
        for outer_index_1 in range(0, len(collect_to_calculate_average)):
            for outer_index_2 in range(0, len(collect_to_calculate_average)):
                if len(collect_to_calculate_average[outer_index_2]) < len(collect_to_calculate_average[outer_index_1]):
                    while len(collect_to_calculate_average[outer_index_2]) < len(collect_to_calculate_average[outer_index_1]):
                        collect_to_calculate_average[outer_index_2].append(0)

        number_of_measurements = len(collect_to_calculate_average)
        measurements_index = 0
        length_of_each_measurement = len(collect_to_calculate_average[measurements_index])
        rtt_index = 0
        rtt = 0
        count_of_zeros = 0

        while rtt_index < length_of_each_measurement:
            while measurements_index < number_of_measurements:
                # current_measurement_index = len(collect_to_calculate_average[measurements_index])
                # if rtt_index <= current_measurement_index:
                rtt += collect_to_calculate_average[measurements_index][rtt_index]
                if (collect_to_calculate_average[measurements_index][rtt_index] == 0) or (measurements_index == 0 and rtt == 0):
                    count_of_zeros += 1
                measurements_index += 1
            if number_of_measurements != count_of_zeros:
                average_median_rtt.append(rtt/(len(collect_to_calculate_average) - count_of_zeros))
            else:
                average_median_rtt.append(0)
            rtt = 0
            measurements_index = 0
            count_of_zeros = 0
            rtt_index += 1

        # combined_rtts = map(sum, zip(*collect_to_calculate_average))
        # average_median_rtt = [median_rtt / len(collect_to_calculate_average) for median_rtt in combined_rtts]
        return average_median_rtt