<template>
    <v-container>
        <v-row>
            <v-col cols="12">
                <h3 class="text-h4 mb-4">Аналитика</h3>
                <v-switch
                    v-model="displayModels"
                    :label="`Статистика ${displayModels ? 'моделей' : 'промптов'}`"
                    class="mb-4"
                ></v-switch>
            </v-col>
        </v-row>

        <!-- Empty state -->
        <v-row v-if="!Object.keys(analyticsData).length">
            <v-col cols="12">
                <v-alert
                    type="info"
                    variant="tonal"
                    icon="mdi-database-off"
                >
                    Жалоб нет. Опять кто-то <v-code>drop database prod</v-code> выполнил?
                </v-alert>
            </v-col>
        </v-row>

        <!-- Data visualization -->
        <template v-else>
            <!-- Summary Cards -->
            <v-row>
                <v-col cols="12" md="4">
                    <v-card>
                        <v-card-text>
                            <div class="text-h6">Всего записей</div>
                            <div class="text-h4">{{ totalReports }}</div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="4">
                    <v-card>
                        <v-card-text>
                            <div class="text-h6">{{ displayModels ? 'Моделей' : 'Промптов' }}</div>
                            <div class="text-h4">{{ Object.keys(analyticsData).length }}</div>
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="4">
                    <v-card>
                        <v-card-text>
                            <div class="text-h6">Типов жалоб</div>
                            <div class="text-h4">{{ uniqueReasonTypes.length }}</div>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Charts -->
            <v-row class="mt-4">
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title>Распределение по типам жалоб</v-card-title>
                        <v-card-text>
                            <Pie
                                v-if="chartData.datasets"
                                :data="chartData"
                                :options="chartOptions"
                            />
                        </v-card-text>
                    </v-card>
                </v-col>
                <v-col cols="12" md="6">
                    <v-card>
                        <v-card-title class="d-flex flex-wrap align-center">
                            <span class="mr-auto">Топ {{ displayModels ? 'моделей' : 'промптов' }}</span>
                            <v-select
                                v-model="selectedMetric"
                                :items="metricOptions"
                                density="compact"
                                hide-details
                                class="ml-4"
                                style="max-width: 200px"
                            ></v-select>
                        </v-card-title>
                        <v-card-text>
                            <Bar
                                v-if="barChartData.datasets"
                                :data="barChartData"
                                :options="barChartOptions"
                            />
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>

            <!-- Detailed Table -->
            <v-row class="mt-4">
                <v-col cols="12">
                    <v-card>
                        <v-card-title>
                            Детальная статистика
                            <v-text-field
                                v-model="search"
                                append-icon="mdi-magnify"
                                label="Поиск"
                                single-line
                                hide-details
                                density="compact"
                                class="mt-4"
                            ></v-text-field>
                        </v-card-title>
                        <v-card-text>
                            <v-data-table
                                :headers="tableHeaders"
                                :items="tableItems"
                                :search="search"
                                class="elevation-1"
                            >
                                <template #[`item.total`]="{ item }">
                                    <v-chip
                                        :color="getStatusColor(item.total)"
                                        text-color="white"
                                    >
                                        {{ item.total }}
                                    </v-chip>
                                </template>
                            </v-data-table>
                        </v-card-text>
                    </v-card>
                </v-col>
            </v-row>
        </template>
    </v-container>
</template>

<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue';
import { fetch_data } from '../helpers';
import { Config } from '../settings';
import { Pie, Bar } from 'vue-chartjs';
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement
} from 'chart.js';

interface DataTableHeader {
    key: string
    title: string
    align?: 'start' | 'end' | 'center'
    sortable?: boolean
    width?: string | number
}
interface ReportStats {
    [reason: string]: number;
}
interface AnalyticsData {
    [modelOrPrompt: string]: ReportStats;
}
interface TableItem {
    name: string;
    total: number;
    [reason: string]: number | string;
}

// Register ChartJS components
ChartJS.register(
    Title,
    Tooltip,
    Legend,
    ArcElement,
    CategoryScale,
    LinearScale,
    BarElement
);

const displayModels = ref(true);
const analyticsData = ref<AnalyticsData>({});
const search = ref('');

// Fetch data
onMounted(updateAnalyticsData);

async function updateAnalyticsData() {
    const endpoint = displayModels.value ? 'models-stats' : 'prompts-stats';
    const response = await fetch_data(`${Config.backend_address}/analytics/${endpoint}/`);
    if (!response) return;
    analyticsData.value = response;
}

// Computed properties
const uniqueReasonTypes = computed(() => {
    const reasons = new Set();
    Object.values(analyticsData.value).forEach((stats: any) => {
        Object.keys(stats).forEach(reason => reasons.add(reason));
    });
    return Array.from(reasons);
});

const totalReports = computed(() => {
    let total = 0;
    Object.values(analyticsData.value).forEach((stats: any) => {
        Object.values(stats).forEach((value: unknown) => {
            total += value as number;
        });
    });
    return total;
});

// Table data
const tableHeaders = computed<DataTableHeader[]>(() => {
    const headers: DataTableHeader[] = [
        {
            title: displayModels.value ? 'Модель' : 'Промпт',
            key: 'name',
            align: 'start',
            sortable: true
        },
        ...uniqueReasonTypes.value.map((reason): DataTableHeader => ({
            title: String(reason),
            key: String(reason),
            align: 'center',
            sortable: true
        })),
        {
            title: 'Всего',
            key: 'total',
            align: 'center',
            sortable: true
        }
    ];

    return headers;
});


const tableItems = computed(() => {
    return Object.entries(analyticsData.value).map(([name, stats]) => {
        const total = Object.values(stats as ReportStats).reduce((sum, curr) => sum + curr, 0);
        const item = {
            name,
            ...stats,
            total
        };
        return item;
    });
});


// Chart data
const chartData = computed(() => {
    const labels = uniqueReasonTypes.value;
    const data = labels.map((reason: unknown) => {
        return Object.values(analyticsData.value).reduce((sum: number, stats: any) => {
            return sum + (stats[reason as string] || 0);
        }, 0);
    });

    return {
        labels,
        datasets: [{
            data,
            backgroundColor: [
                '#FF6384',
                '#36A2EB',
                '#FFCE56',
                '#4BC0C0',
                '#9966FF',
                '#FF9F40'
            ]
        }]
    };
});

const selectedMetric = ref('total');
const metricOptions = computed(() => {
    return [
        { title: 'Всего', value: 'total' },
        ...uniqueReasonTypes.value.map(reason => ({
            title: reason,
            value: String(reason)
        }))
    ];
});

const barChartData = computed(() => {
    const metric = selectedMetric.value;
    let sortedItems: TableItem[];

    if (metric === 'total') {
        sortedItems = [...tableItems.value]
            .sort((a, b) => b.total - a.total)
            .slice(0, 5);
    } else {
        sortedItems = [...tableItems.value]
            .sort((a, b) => {
                const key = metric as keyof TableItem;
                // @ts-ignore
                return ((b[key] as number) || 0) - ((a[key] as number) || 0);
            })
            .slice(0, 5);
    }

    return {
        labels: sortedItems.map(item => item.name),
        datasets: [{
            label: metric === 'total'
                ? 'Количество жалоб'
                : `Количество жалоб типа "${metric}"`,
            data: sortedItems.map(item =>
                metric === 'total' ? item.total : ((item[metric as keyof TableItem] as number) || 0)
            ),
            backgroundColor: '#36A2EB'
        }]
    };

});

// Chart options
const chartOptions = {
    responsive: true,
    plugins: {
        legend: {
            position: 'right' as const
        }
    }
};

const barChartOptions = {
    responsive: true,
    plugins: {
        legend: {
            display: false
        }
    },
    scales: {
        y: {
            beginAtZero: true
        }
    }
};

// Utilities
function getStatusColor(total: number) {
    if (total > 100) return 'error';
    if (total > 50) return 'warning';
    return 'success';
}

watch(displayModels, updateAnalyticsData);
</script>