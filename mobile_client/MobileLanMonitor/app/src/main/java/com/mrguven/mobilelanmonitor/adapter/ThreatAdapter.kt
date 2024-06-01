package com.mrguven.mobilelanmonitor.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.mrguven.mobilelanmonitor.R
import com.mrguven.mobilelanmonitor.model.Threat

class ThreatAdapter : RecyclerView.Adapter<ThreatAdapter.ThreatViewHolder>() {

    private var threats: List<Threat> = listOf()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ThreatViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_threat, parent, false)
        return ThreatViewHolder(view)
    }

    override fun onBindViewHolder(holder: ThreatViewHolder, position: Int) {
        val threat = threats[position]
        holder.bind(threat)
    }

    override fun getItemCount(): Int {
        return threats.size
    }

    fun submitList(threatList: List<Threat>) {
        threats = threatList
        notifyDataSetChanged()
    }

    class ThreatViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val ipTextView: TextView = itemView.findViewById(R.id.ipTextView)
        private val timestampTextView: TextView = itemView.findViewById(R.id.timestampTextView)
        private val threatTextView: TextView = itemView.findViewById(R.id.threatTextView)

        fun bind(threat: Threat) {
            ipTextView.text = threat.ip
            timestampTextView.text = "Timestamp: ${threat.timestamp}"
            threatTextView.text = "Threat: ${threat.is_threat}"
        }
    }
}
