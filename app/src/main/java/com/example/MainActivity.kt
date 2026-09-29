package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocalHospital
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.MyApplicationTheme

data class ScenarioCard(
    val name: String,
    val ageGender: String,
    val category: String,
    val setting: String,
    val difficulty: String,
    val summary: String
)

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    enableEdgeToEdge()
    setContent {
      MyApplicationTheme {
        Scaffold(
          modifier = Modifier.fillMaxSize().testTag("caresim_root"),
          topBar = {
            @OptIn(ExperimentalMaterial3Api::class)
            TopAppBar(
              title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                  Icon(
                    Icons.Default.LocalHospital,
                    contentDescription = "CareSim Logo",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(28.dp)
                  )
                  Spacer(Modifier.width(8.dp))
                  Text(
                    "CareSim AI",
                    fontWeight = FontWeight.Bold,
                    fontSize = 20.sp
                  )
                }
              },
              colors = TopAppBarDefaults.topAppBarColors(
                containerColor = MaterialTheme.colorScheme.surface
              )
            )
          }
        ) { innerPadding ->
          CareSimOverviewScreen(modifier = Modifier.padding(innerPadding))
        }
      }
    }
  }
}

@Composable
fun CareSimOverviewScreen(modifier: Modifier = Modifier) {
  val scenarios = remember {
    listOf(
      ScenarioCard(
        name = "Margaret Dawson",
        ageGender = "82y, Female",
        category = "Frailty and fall risk",
        setting = "Community / Home Visit",
        difficulty = "Intermediate",
        summary = "Multifactorial fall assessment, postural hypotension, polypharmacy, and living hazards."
      ),
      ScenarioCard(
        name = "Arthur Chen",
        ageGender = "68y, Male",
        category = "Complex long-term conditions",
        setting = "Primary Care Clinic",
        difficulty = "Advanced",
        summary = "Type 2 Diabetes, CKD Stage 3a, nocturnal neuropathy, and Metformin GI intolerance."
      ),
      ScenarioCard(
        name = "Liam O'Connor",
        ageGender = "34y, Male",
        category = "Mental health and social isolation",
        setting = "Community Mental Health",
        difficulty = "Advanced",
        summary = "Major reactive depression, bereavement, alcohol coping, and passive suicidal ideation screening."
      ),
      ScenarioCard(
        name = "Eleanor Vance",
        ageGender = "74y, Female",
        category = "End-of-life and palliative care",
        setting = "Hospice Day Care",
        difficulty = "Intermediate",
        summary = "Metastatic lung cancer, breakthrough bone pain, opioid fears, and advance care planning."
      ),
      ScenarioCard(
        name = "Fatima Al-Mansoor",
        ageGender = "59y, Female",
        category = "Integrated care coordination",
        setting = "Intermediate Care",
        difficulty = "Intermediate",
        summary = "Left MCA ischemic stroke recovery, mild expressive aphasia, and family caregiver strain."
      )
    )
  }

  LazyColumn(
    modifier = modifier
      .fillMaxSize()
      .padding(horizontal = 16.dp),
    verticalArrangement = Arrangement.spacedBy(14.dp)
  ) {
    item {
      Card(
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        modifier = Modifier.fillMaxWidth().testTag("hero_banner")
      ) {
        Column(modifier = Modifier.padding(16.dp)) {
          Text(
            "Agentic Virtual Patient Simulation",
            fontWeight = FontWeight.Bold,
            fontSize = 17.sp,
            color = MaterialTheme.colorScheme.onPrimaryContainer
          )
          Spacer(Modifier.height(4.dp))
          Text(
            "Powered by Python, Streamlit, and Groq API with 5 specialized clinical simulation scenarios, multi-turn progressive disclosure, and 6-domain rubric evaluations.",
            fontSize = 13.sp,
            color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.85f)
          )
        }
      }
    }

    item {
      Text(
        "Virtual Patient Library",
        fontWeight = FontWeight.Bold,
        fontSize = 18.sp,
        modifier = Modifier.padding(vertical = 4.dp)
      )
    }

    items(scenarios) { sc ->
      Card(
        shape = RoundedCornerShape(10.dp),
        modifier = Modifier.fillMaxWidth().testTag("patient_card_${sc.name.replace(" ", "_")}"),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
      ) {
        Column(modifier = Modifier.padding(14.dp)) {
          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Column {
              Text(sc.name, fontWeight = FontWeight.Bold, fontSize = 16.sp)
              Text(sc.ageGender, fontSize = 12.sp, color = MaterialTheme.colorScheme.outline)
            }
            Surface(
              shape = RoundedCornerShape(12.dp),
              color = MaterialTheme.colorScheme.primary.copy(alpha = 0.15f)
            ) {
              Text(
                sc.difficulty,
                fontSize = 11.sp,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
              )
            }
          }
          Spacer(Modifier.height(6.dp))
          Text(
            "🏥 ${sc.setting} • ${sc.category}",
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.secondary,
            fontWeight = FontWeight.Medium
          )
          Spacer(Modifier.height(4.dp))
          Text(sc.summary, fontSize = 13.sp)
        }
      }
    }

    item {
      Card(
        shape = RoundedCornerShape(8.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        modifier = Modifier.fillMaxWidth().padding(bottom = 24.dp)
      ) {
        Column(modifier = Modifier.padding(12.dp)) {
          Text(
            "⚠️ Educational Notice",
            fontWeight = FontWeight.SemiBold,
            fontSize = 13.sp,
            color = MaterialTheme.colorScheme.error
          )
          Spacer(Modifier.height(4.dp))
          Text(
            "CareSim AI is strictly an educational simulation platform. All patient profiles and clinical findings are fictional. In a real medical emergency, call 911/999/112.",
            fontSize = 12.sp,
            color = MaterialTheme.colorScheme.onSurfaceVariant
          )
        }
      }
    }
  }
}

