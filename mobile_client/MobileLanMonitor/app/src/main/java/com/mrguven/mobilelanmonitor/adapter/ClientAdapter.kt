package com.mrguven.mobilelanmonitor.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.RecyclerView
import com.mrguven.mobilelanmonitor.databinding.ItemClientBinding
import com.mrguven.mobilelanmonitor.model.Client
import com.mrguven.mobilelanmonitor.api.ApiService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class ClientAdapter(private val apiService: ApiService) : RecyclerView.Adapter<ClientAdapter.ClientViewHolder>() {

    private var clients: List<Client> = listOf()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ClientViewHolder {
        val binding = ItemClientBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ClientViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ClientViewHolder, position: Int) {
        val client = clients[position]
        holder.bind(client)
    }

    override fun getItemCount(): Int {
        return clients.size
    }

    fun submitList(clientList: List<Client>) {
        clients = clientList
        notifyDataSetChanged()
    }

    inner class ClientViewHolder(private val binding: ItemClientBinding) : RecyclerView.ViewHolder(binding.root) {

        init {
            itemView.setOnClickListener {
                if (binding.expandableLayout.visibility == View.GONE) {
                    binding.expandableLayout.visibility = View.VISIBLE
                } else {
                    binding.expandableLayout.visibility = View.GONE
                }
            }

            binding.connectButton.setOnClickListener {
                val client = clients[adapterPosition]
                val command = if (client.connected_to_internet) "go_offline" else "go_online"
                sendCommand(client.ip, command)
            }
        }

        fun bind(client: Client) {
            val uploadSpeedMB = client.upload_speed / (1024 * 1024) // Byte'dan MB'a dönüştürme
            val downloadSpeedMB = client.download_speed / (1024 * 1024) // Byte'dan MB'a dönüştürme


            binding.ipTextView.text = client.ip
            binding.connectedTextView.text = "Connected to Internet: ${client.connected_to_internet}"
            binding.uploadTextView.text = String.format("Upload: %.2f MB", uploadSpeedMB)
            binding.downloadTextView.text = String.format("Download: %.2f MB", downloadSpeedMB)
            binding.cpuUsageTextView.text =  String.format("CPU Usage: %.2f%%", client.cpu_usage)
            binding.memoryUsageTextView.text =  String.format("Memory Usage: %.2f%%", client.memory_usage)
            binding.packetSentTextView.text = String.format("Packet Sent: %d", client.packet_sent)
            binding.packetReceiveTextView.text = String.format("Packet Receive: %d", client.packet_recv)
            binding.errorInTextView.text = String.format("Error In: %d", client.error_in)
            binding.errorOutTextView.text = String.format("Error Out: %d", client.error_out)
            binding.dropInTextView.text = String.format("Drop In: %d", client.drop_in)
            binding.dropOutTextView.text = String.format("Drop Out: %d", client.drop_out)
            binding.connectButton.text = if (client.connected_to_internet) "Disconnect" else "Connect"
        }

        private fun sendCommand(ip: String, command: String) {
            CoroutineScope(Dispatchers.IO).launch {
                try {
                    apiService.sendCommand(ip, mapOf("command" to command))
                } catch (e: Exception) {
                    // Hata yönetimi
                }
            }
        }
    }
}
